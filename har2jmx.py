"""Convert a HAR file to a JMeter test plan


Parse <filename>.har and write <filename>.jmx
"""
from argparse import ArgumentParser
import xmlformatter
from harpy.har import Har
from jinja2 import Environment, PackageLoader
from urlparse import urlparse


env = Environment(loader=PackageLoader('har2jmx', '.'))


def make_test_plan(har, access_token):
    """
    :param har: the parsed HAR object
    :return: test plan
    """
    requests = []
    for entry in har.entries:
        jmx_request = make_request(entry.request)
        if jmx_request:
            requests.append(jmx_request)

    t = env.get_template('test_plan.j2')
    xml = t.render(dict(access_token=access_token,
                        requests=requests))
    formatter = xmlformatter.Formatter(indent="2",
                                       indent_char=" ",
                                       encoding_output="ISO-8859-1",
                                       preserve=["literal"])
    result = formatter.format_string(xml)

    return xml


def make_request(har_request):
    parsed_url = urlparse(har_request.url)
    arguments = []
    path = parsed_url.path
    if not path.startswith('/v2'):
        return None
    test_name = path[1:]
    host = parsed_url.netloc

    for arg in har_request.query_string:
        jmx_arg = make_argument(arg)
        arguments.append(jmx_arg)

    t = env.get_template('request.j2')
    result = t.render(dict(test_name=test_name,
                           host=host,
                           path=path,
                           arguments=arguments))

    return result


def make_argument(har_argument):
    t = env.get_template('argument.j2')
    arg_name = har_argument.name
    arg_value = har_argument.value
    d = dict(arg_name=arg_name,
             arg_value=arg_value)
    result = t.render(d)

    return result


def main(har_file, access_token, output_file):
    har = Har(har_file)
    test_plan = make_test_plan(har, access_token)
    open(output_file, 'w').write(test_plan)
    print 'Done.'


def options():
    parser = ArgumentParser()
    parser.add_argument('--har-file', required=True)
    parser.add_argument('--access-token', required=True)
    parser.add_argument('--output-file', required=True)
    return parser.parse_args()

if __name__ == '__main__':
    o = options()
    main(o.har_file, o.access_token, o.output_file)
