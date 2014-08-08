import sys
from workflow import Workflow
import xmlrpclib

server = xmlrpclib.Server("http://api.opensubtitles.org/xml-rpc")


def login_token():
    response = server.LogIn("", "", "fr", "MyAPP V2")
    login_token = str(response["token"])
    return login_token


def format_subtitle(document):
    episode = ''
    if 'SeriesEpisode' in document and 'SeriesEpisode' in document and \
       int(document['SeriesEpisode']) > 0 and \
       int(document['SeriesSeason']) > 0:
        episode = ' S{0}E{0}'.format(
            "%02d" % int(document['SeriesSeason']),
            "%02d" % int(document['SeriesEpisode'])
        )

    return '{0}{1} - {2} - {3}'.format(
        document['MovieName'],
        episode,
        document['MovieYear'],
        document['ISO639']
    )


def main(wf):
    args = wf.args
    query = args[0]
    cached_login_token = wf.cached_data('login', login_token, max_age=60)

    results = wf.cached_data(
        query,
        lambda: server.SearchSubtitles(
            cached_login_token, [{'query': query}]
        )['data'],
        max_age=3600
    )

    if not results or len(results) == 0:
        title = 'No results'
        subtitle = 'We could not fetch any subtitles for \'{0}\''.format(query)
        wf.add_item(title, subtitle)
    else:
        for document in results:
            wf.add_item(
                title=document['SubFileName'],
                subtitle=format_subtitle(document),
                arg=document['ZipDownloadLink'],
                valid=True
            )

    wf.send_feedback()

if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
