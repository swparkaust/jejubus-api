import datetime
import difflib
import inquirer
import os
import re
import requests
import requests_cache
from bs4 import BeautifulSoup
from openpyxl import load_workbook
from tqdm import tqdm

from django.conf import settings
from django.core.management.base import BaseCommand

from main.models import Route, Station, StationOtherName, Time


def download(url: str, dest_folder: str):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)  # create folder if it does not exist

    filename = url.split('/')[-1].replace(
        " ", "_") + ".xlsx"  # be careful with file names
    file_path = os.path.join(dest_folder, filename)

    r = requests.get(url, stream=True)
    if r.ok:
        print("saving to", os.path.abspath(file_path))
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
    else:  # HTTP status code 4XX/5XX
        print("Download failed: status code {}\n{}".format(r.status_code, r.text))


def extract_node_name_from_string(s):
    pattern = r'(.*?)(?:\(.*\))?(?:\[.*\])?$'
    matches = re.findall(pattern, s)
    if not matches:
        return s
    else:
        return matches[0]


def extract_route_number_from_string(s):
    pattern = r'\d[0-9\-]*'
    matches = re.findall(pattern, s)
    if not matches:
        return s.replace('\n', '').replace('\r', '')
    else:
        return matches[0]


def extract_time_from_string(s):
    pattern = r'(2[0-3]|[01]?[0-9])(?::|;)([0-5]?[0-9])'
    matches = re.findall(pattern, s)
    if not matches:
        return None
    else:
        return datetime.time(int(matches[0][0]), int(matches[0][1]), 0)


def get_all_route_nodes(city_code, route_id):
    url = 'http://openapi.tago.go.kr/openapi/service/BusRouteInfoInqireService/getRouteAcctoThrghSttnList'
    queryParams = '?ServiceKey=' + settings.BUS_INFO_API_KEY + \
        '&numOfRows=100&pageNo=1&cityCode=' + city_code + '&routeId=' + route_id

    request = requests.get(url + queryParams)
    response_body = request.text
    soup = BeautifulSoup(response_body, 'html.parser')

    found_values = soup.find_all('item')
    route_nodes = []
    for x in found_values:
        tags = [
            'routeid', 'nodeid', 'nodenm', 'nodeord', 'gpslati', 'gpslong', 'updowncd'
        ]
        route_node = {}
        for tag in tags:
            route_node[tag] = '{}'.format(x.find(tag).text)
        route_nodes.append(route_node)
    return route_nodes


def get_node_ids(city_code, node_name):
    url = 'http://openapi.tago.go.kr/openapi/service/BusSttnInfoInqireService/getSttnNoList'
    queryParams = '?ServiceKey=' + settings.BUS_INFO_API_KEY + \
        '&cityCode=' + city_code + '&nodeNm=' + node_name

    request = requests.get(url + queryParams)
    response_body = request.text
    soup = BeautifulSoup(response_body, 'html.parser')

    found_values = soup.find_all('nodeid')
    return [x.text for x in found_values]


def get_route_node(city_code, route_id, node_name, start=None, end=None, interactive=True):
    sl = slice(start, end)
    all_route_nodes = get_all_route_nodes(city_code, route_id)[sl]
    for node_id in get_node_ids(city_code, node_name):
        for route_node in all_route_nodes:
            if route_node['nodeid'] == node_id:
                return route_node
    station_other_names = StationOtherName.objects.filter(
        other_station_name=node_name)
    if station_other_names.exists():
        for o in station_other_names:
            for route_node in all_route_nodes:
                if route_node['nodeid'] == o.station_id:
                    return route_node
    if interactive:
        choices = [x['nodenm'] for x in all_route_nodes]
        matches = difflib.get_close_matches(
            node_name, choices, len(choices), 0)
        questions = [
            inquirer.List(
                'node_name',
                message="What node is " + node_name + "?",
                choices=matches, ),
        ]
        answers = inquirer.prompt(questions)
        if answers is None:
            return None
        else:
            selected_node = all_route_nodes[choices.index(
                answers["node_name"])]
            station_other_name = StationOtherName(
                station_id=selected_node['nodeid'], other_station_name=node_name)
            station_other_name.save()
            return selected_node
    else:
        return None


def get_route_nodes(city_code, route_id, node_names):
    route_nodes = []
    last = None
    for i, node_name in enumerate(node_names):
        if last is None:
            route_node = get_route_node(
                city_code, route_id, node_name, 0, 1, False)
        else:
            route_node = get_route_node(
                city_code, route_id, node_name, last, -(len(node_names) - i - 1) or None, False)
        if route_node is None:
            continue
        route_nodes.append(route_node)
        last = int(route_node['nodeord'])
    return route_nodes


def get_route(city_code, route_number, node_names):
    url = 'http://openapi.tago.go.kr/openapi/service/BusRouteInfoInqireService/getRouteNoList'
    queryParams = '?ServiceKey=' + settings.BUS_INFO_API_KEY + \
        '&cityCode=' + city_code + '&routeNo=' + route_number

    request = requests.get(url + queryParams)
    response_body = request.text
    soup = BeautifulSoup(response_body, 'html.parser')

    found_values = soup.find_all('item')
    if found_values:
        best_match = max(found_values, key=lambda result: difflib.SequenceMatcher(None, [
                         x['nodenm'] for x in get_route_nodes(city_code, result.find('routeid').text, node_names)], node_names).ratio())
        all_route_nodes = get_all_route_nodes(
            city_code, best_match.find('routeid').text)
        if best_match.find('startnodenm').text != node_names[0] and not StationOtherName.objects.filter(other_station_name=node_names[0]).exists():
            route_start_node = all_route_nodes[0]
            start_station_other_name = StationOtherName(
                station_id=route_start_node['nodeid'], other_station_name=node_names[0])
            start_station_other_name.save()
        if best_match.find('endnodenm').text != node_names[-1] and not StationOtherName.objects.filter(other_station_name=node_names[-1]).exists():
            route_end_node = all_route_nodes[-1]
            end_station_other_name = StationOtherName(
                station_id=route_end_node['nodeid'], other_station_name=node_names[-1])
            end_station_other_name.save()
        tags = ['routeid', 'routeno', 'routetp', 'endnodenm', 'startnodenm']
        route = {}
        for tag in tags:
            route[tag] = '{}'.format(best_match.find(tag).text)
        return route
    else:
        return None


class Command(BaseCommand):

    help = 'Updates the database via Bus Info API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-history',
            action='store_true',
            dest='clear_history',
            help='Clean station find history',
        )
        parser.add_argument(
            '--clear-db',
            action='store_true',
            dest='clear_db',
            help='Clear database before adding new objects',
        )
        parser.add_argument(
            '--noinput',
            action='store_false',
            dest='interactive',
            default=True,
            help='Do NOT prompt the user for input of any kind.',
        )

    def handle(self, *args, **options):
        requests_cache.install_cache('jejubus_cache')

        for route_type in settings.ROUTE_TYPES:
            download(
                "http://bus.jeju.go.kr/publicTrafficInformation/downloadSchedule/" +
                route_type,
                dest_folder="temp")

        if options['clear_history']:
            self.stdout.write('Clearing station find history ... ', ending='')
            StationOtherName.objects.all().delete()
            self.stdout.write('done.')

        if options['clear_db']:
            self.stdout.write('Clearing database ... ', ending='')
            Time.objects.all().delete()
            Route.objects.all().delete()
            Station.objects.all().delete()
            self.stdout.write('done.')

        with os.scandir("temp") as it:
            for entry in tqdm(it):
                if entry.name.endswith(".xlsx") and entry.is_file():
                    self.stdout.write("{} {}".format(entry.name, entry.path))

                    wb = load_workbook(filename=entry.path, data_only=True)

                    for sheet in tqdm(wb.worksheets):
                        route_number = sheet['B2'].value if sheet['A1'].value is None else sheet[
                            'A1'].value
                        route_number = extract_route_number_from_string(
                            route_number)

                        node_names = []
                        row = 7 if sheet['A1'].value is None else 6
                        for cell in sheet[row]:
                            node_name = cell.value
                            if node_name is not None:
                                node_name = "".join(node_name.split())
                                if node_name != "노선번호" and node_name != "구분" and node_name != "비고":
                                    node_name = extract_node_name_from_string(
                                        node_name)
                                    node_names.append(node_name)

                        route = get_route(
                            settings.CITY_CODE_JEJU, route_number, node_names)
                        if route is None:
                            continue
                        route_obj = Route(route_type=os.path.splitext(entry.name)[
                                          0], route_id=route['routeid'], route_number=route_number, start_station_name=route['startnodenm'], end_station_name=route['endnodenm'])
                        route_obj.save()

                        route_number_column = None
                        last = None
                        i = 0
                        row = sheet[7] if sheet['A1'].value is None else sheet[6]
                        for cell in row:
                            node_name = cell.value
                            if node_name is not None:
                                node_name = "".join(node_name.split())
                                if node_name == "노선번호":
                                    route_number_column = cell.column_letter
                                elif node_name != "구분" and node_name != "비고":
                                    node_name = extract_node_name_from_string(
                                        node_name)
                                    if last is None:
                                        route_node = get_route_node(
                                            settings.CITY_CODE_JEJU, route['routeid'], node_name, 0, 1, options['interactive'])
                                    else:
                                        route_node = get_route_node(
                                            settings.CITY_CODE_JEJU, route['routeid'], node_name, last, -(len(node_names) - i - 1) or None, options['interactive'])
                                    if route_node is None:
                                        continue
                                    node_name = route_node['nodenm']
                                    last = int(route_node['nodeord'])
                                    i += 1
                                    station = Station(
                                        station_id=route_node['nodeid'], station_name=node_name)
                                    station.save()
                                    for cell2 in sheet[cell.column][cell.row + 1:]:
                                        time = cell2.value
                                        if time is not None:
                                            if isinstance(time, str):
                                                time = extract_time_from_string(
                                                    time)
                                                if time is None:
                                                    continue
                                            elif type(time) is not datetime.time:
                                                continue
                                            if route_number_column is not None:
                                                cell_name = "{}{}".format(
                                                    route_number_column, cell2.row)
                                                route_number = sheet[cell_name].value
                                                route_number = extract_route_number_from_string(
                                                    str(route_number))

                                                route = get_route(
                                                    settings.CITY_CODE_JEJU, route_number, node_names)
                                                if route is None:
                                                    continue
                                                route_obj = Route(route_type=os.path.splitext(entry.name)[
                                                                  0], route_id=route['routeid'], route_number=route_number, start_station_name=route['startnodenm'], end_station_name=route['endnodenm'])
                                                route_obj.save()
                                            time_obj = Time(
                                                route=route_obj, station=station, time=time)
                                            time_obj.save()

        self.stdout.write(self.style.SUCCESS(
            'Successfully updated the database'))
