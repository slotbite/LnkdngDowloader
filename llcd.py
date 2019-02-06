# chcp 65001
# set PYTHONIOENCODING = utf-
# working on python 2.7
import cookielib
import os
import urllib
import urllib2
import sys
import config
import requests
import re
from bs4 import BeautifulSoup
import config
import time
import locale
# print locale.getdefaultlocale()[1]

from googletrans import Translator
import sys
reload(sys)


# print locale.getdefaultlocale()[1]


def login():
    cookie_filename = 'cookies.txt'

    cookie_jar = cookielib.MozillaCookieJar(cookie_filename)

    opener = urllib2.build_opener(
        urllib2.HTTPRedirectHandler(),
        urllib2.HTTPHandler(debuglevel=0),
        urllib2.HTTPSHandler(debuglevel=0),
        urllib2.HTTPCookieProcessor(cookie_jar)
    )

    html = load_page(opener, 'https://www.linkedin.com/')
    soup = BeautifulSoup(html, 'html.parser')
    csrf = soup.find(id='loginCsrfParam-login')['value']

    login_data = urllib.urlencode({
        'session_key': config.USERNAME,
        'session_password': config.PASSWORD,
        'loginCsrfParam': csrf,
    })

    load_page(opener, 'https://www.linkedin.com/uas/login-submit', login_data)

    try:
        cookie = cookie_jar._cookies['.www.linkedin.com']['/']['li_at'].value
    except:
        sys.exit(0)

    cookie_jar.save()
    os.remove(cookie_filename)

    return cookie


def authenticate():
    try:
        session = login()
        if len(session) == 0:
            sys.exit('[!] Imposible ingresar a LinkedIn.com')
        print '[*] Conectando API Linkeding [OK]'
        cookies = dict(li_at=session)
    except Exception, e:
        sys.exit('[!] No se ha podido establecer la conexion. %s' % e)
    return cookies


def load_page(opener, url, data=None):
    try:
        response = opener.open(url)
    except:
        print '[Fatal] Tu IP ha sido bloqueada temporalmente'

    try:
        if data is not None:
            response = opener.open(url, data)
        else:
            response = opener.open(url)
        return ''.join(response.readlines())
    except:
        print '[!] Error en el envio de los datos'
        sys.exit(0)


def download_file(url, file_path, file_name):
    # print file_path + '/' + file_name ## mucha wea
    sys.setdefaultencoding('utf-8')

    reply = requests.get(url, stream=True)
    if not os.path.exists(file_path):
        os.makedirs(file_path)

    # se agrega por problemas con algunos video o el largo del nombre
    try:
        # print '     Video ?: ' + \
        #    str(os.path.exists(file_path + '/' + file_name))
        with open(file_path + '/' + file_name, 'wb') as f:
            for chunk in reply.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        f.close()

    except (OSError, IOError) as exc:
        print("[NOPE] - - Comprueba el video " +
              file_name + '  {}'.format(exc))
        pass


def clean_dir_name(dir_name):
    # Remove starting digit and dot (e.g '1. A' -> 'A')
    # Remove bad characters         (e.g 'A: B' -> 'A B')
    no_digit = re.sub(r'^\d+\.', "", dir_name)
    no_bad_chars = re.sub(r'[\\:<>"/|?*]', "", no_digit)
    return no_bad_chars.strip()


def download_subtitles(file_path, file_name, descargar):

    # from translate import Translator
    # translator = Translator(from_lang="english", to_lang="spanish")

    translator = Translator()

    # print file_path, file_name
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    # srt needs start and end time, while LinkedIn is only providing start time. So I use end-time of a subtitle = start time of the next subtitle.
    try:
        with open(file_path + '/' + file_name, 'a') as subtitle_file:
            index_next_subtitle = 1
            for subtitle in subtitles:
                # print('Next-Index: "%i"') % index_next_subtitle
                transcriptStartAt = milliseconds = subtitle['transcriptStartAt']
                # for last subtitle (which hasn't a successor) we use an end time that is probably longer than the video has now left (+5 seconds)
                # detecting last subtitle / list index out of boundary
                if (index_next_subtitle == len(subtitles)):
                    transcriptEndAt = transcriptStartAt + 5000
                else:
                    transcriptEndAt = milliseconds = subtitles[index_next_subtitle]['transcriptStartAt']
                caption = subtitle['caption']
                # print caption
                if(descargar):
                    caption = translator.translate(
                        caption, src='auto', dest='es').text
                # print translation
                # write to file (line for line)
                subtitle_file.write(str(index_next_subtitle)+'\n')
                # subtitle_file.write()
                subtitle_file.write(str(to_hhmmssms(transcriptStartAt)))
                subtitle_file.write(' --> ')
                subtitle_file.write(str(to_hhmmssms(transcriptEndAt))+'\n')
                # subtitle_file.write('\n')
                # subtitle_file.write(caption)
                subtitle_file.write(caption+'\n\n')
                # subtitle_file.write('\n\n')
                index_next_subtitle += 1
        subtitle_file.close()

    except (OSError, IOError) as exc:
        print('[NOPE] -- Comprueba el subtitulo ' +
              file_name+'   {}'.format(exc))
        pass
        # os.remove(file_path + '/' + file_name)
        # print(e)


def to_hhmmssms(ms):
    sec, ms = divmod(ms, 1000)
    min, sec = divmod(sec, 60)
    hr, min = divmod(min, 60)
    return "%02d:%02d:%02d,%03d" % (hr, min, sec, ms)


def to_esp(text, traductor, activado):
    sys.setdefaultencoding('iso-8859-1')

    if(activado):
        try:
            return traductor.translate(text, src='auto', dest='es').text
        except (OSError, IOError) as exc:
            print("[SUB] --- Error de traduccion en : "+text+"  {}".format(exc))
            return text

    return text


if __name__ == '__main__':
    print("[Welcome to Linkeding Course Downloader]\n")
    cookies = authenticate()
    headers = {'Csrf-Token': 'ajax:4332914976342601831'}
    cookies['JSESSIONID'] = 'ajax:4332914976342601831'

    file_type_srt = '.srt'

    traducir = False  # cambiar a True para cursos un ingles

    traductor = Translator()

    for course in config.COURSES:
        # print ' new course'
        course_url = 'https://www.linkedin.com/learning-api/detailedCourses' \
                     '??fields=videos&addParagraphsToTranscript=true&courseSlug={0}&q=slugs'.format(
                         course)
        r = requests.get(course_url, cookies=cookies, headers=headers)
        try:
            # course_name = clean_dir_name(r.json()['elements'][0]['title'])
            course_name = clean_dir_name(r.json()['elements'][0]['title'])

        except:
            print r.json()
            if r.json()['status'] == 404:
                print('[!] Server-Reponse: 404. Mostly caused by user failure when providing a wrong course slug in config file.\n[!] Check for errors like: course-title-xyz/setting-up-the-abc. Only course slug is allowed.')
            if r.json()['status'] == 429:
                print("[!] Server-Reponse: 429 (Too Many Requests). Thus your account has been temporarily blocked by LinkedIn.\n[!] Try again in 12 hours. Each new made request in that time will reset and/or double the waiting time.")
            exit(0)
        else:
            course_name = to_esp(course_name, traductor, traducir)
            print('[*] Descargando curso [%s]' % course_name)

            # Material extra -----------------------------------------------------------

            course_description = r.json()['elements'][0]['description']
            fullCourseUnlocked = r.json()['elements'][0]['fullCourseUnlocked']
            course_releasedate_unix = r.json()['elements'][0]['releasedOn']
            course_releasedate = time.strftime(
                "%Y.%m", time.gmtime(course_releasedate_unix / 1000.0))
            # for future use: tag/name of updated-element unknown on LinkedIn Learning so far. If known, use the newer Update date for course-folder instead of old initial release date
            # course_updatedate_unix =
            # course_updatedate_
            # course_folder_path = '%s/%s (%s)' % (base_download_path, course_name, course_releasedate)

            course_folder_path = config.BASE_DOWNLOAD_PATH + \
                '/' + course_name + '/Ejercicios'

            print("[*] Explorando material de apoyo.")

            try:
                exercise_file_name = r.json(
                )['elements'][0]['exerciseFiles'][0]['name']
                exercise_file_url = r.json(
                )['elements'][0]['exerciseFiles'][0]['url']
                exercise_size = (
                    r.json()['elements'][0]['exerciseFiles'][0]['sizeInBytes'])/1024/1024
            except:
                print('[!] El curso no contiene material de apoyo.\n')
            else:
                if os.path.exists(course_folder_path + '/' + exercise_file_name):
                    print('[!] --- Ya se ha descargado [OK]')
                else:
                    print(('[*] --- Descargando (%s MB)' %
                           exercise_size))
                    download_file(exercise_file_url,
                                  course_folder_path, exercise_file_name)
                    print('[*] --- Material de apoyo [OK].')

            chapters = r.json()['elements'][0]['chapters']
            print '[*] Explorando videos'
            print '[*] El curso contiene %d capitulos' % len(chapters)

            # Chapters
            cap = 1
            for chapter in chapters:
                chapter_name = str(
                    cap) + ' ' + to_esp(clean_dir_name(chapter['title']), traductor, traducir)
                # chapter_name = str(cap) + ' '+chapter_name
                cap = cap+1
                videos = chapter['videos']
                file_path = config.BASE_DOWNLOAD_PATH + '/' + course_name + '/' + chapter_name
                # contador de los videos
                vc = 0

                print '[*] --- Capitulo [%s] ' % chapter_name
                print '[*] --- [Contiene %d videos]' % len(videos)

                # Videos
                for video in videos:
                    # video_name = re.sub(r'[\\/*?:"<>|]', "", video['title'])
                    video_name = to_esp(clean_dir_name(
                        video['title']), traductor, traducir)
                    #  video_name = re.sub(ur'[^\x00-\x7F]', u'', video_name)
                    video_slug = video['slug']
                    video_url = 'https://www.linkedin.com/learning-api/detailedCourses' \
                        '?addParagraphsToTranscript=false&courseSlug={0}&q=slugs&resolution=_720&videoSlug={1}'\
                        .format(course, video_slug)
                    r = requests.get(
                        video_url, cookies=cookies, headers=headers)
                    vc += 1

                    # nombre para el  sub
                    file_name = video_name

                    # Descargando videos
                    try:
                        download_url = re.search(
                            '"progressiveUrl":"(.+)","streamingUrl"', r.text).group(1)
                    except:
                        print '[!] ------ Revisa tu subscripcion amigo :( video["%s"]' % video_name
                    else:

                        # print 'Verificando : ' + config.BASE_DOWNLOAD_PATH + '/' + course_name + \
                        #    '/' + chapter_name + '/' + \
                        #    str(vc)+'. '+video_name+'.mp4'
                        if os.path.exists(config.BASE_DOWNLOAD_PATH + '/' + course_name + '/' + chapter_name + '/'+str(vc)+'. '+video_name+'.mp4'):
                            print('[!] ------ Video [%s] ya descargado.' %
                                  video_name)
                        else:
                            # % video_name.decode("utf-8", "ignore")
                            print '[*] ------ Descargando video %s : [%s]' % (
                                str(vc), video_name)

                            download_file(download_url, config.BASE_DOWNLOAD_PATH+'/%s/%s' % (course_name,
                                                                                              chapter_name), '%s. %s.mp4' % (str(vc), video_name))
                            print('[*] ------ Video [OK] ')

                    # Download subtitles
                    try:
                        subtitles = r.json()[
                            'elements'][0]['selectedVideo']['transcript']['lines']

                    except Exception as e:
                        print('[!] ------ Curso sin subtitulos')
                    else:
                        print('[*] ------ Descargando subtitulos...')

                        if os.path.exists(file_path + '/' + str(vc)+'. ' + file_name + file_type_srt):
                            print('[!] ------ Subtitlulo ya descargado.')
                        else:
                            download_subtitles(file_path, str(
                                vc)+'. '+file_name + file_type_srt, traducir)

                            print('[*] ------ Subtitulo [OK] ')

    print '[*] Descargas finalizadas'
