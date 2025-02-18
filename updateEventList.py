# -*- coding: utf-8 -*-
import os
import json
import dateutil.parser
import argparse, sys
import shutil

def get_event_ids (data_path):
    """
        Get event IDs from the list of folders in data folder
    """
    dirlist = [ item for item in os.listdir(data_path) if os.path.isdir(os.path.join(data_path, item)) ]
    return dirlist

def separate_time_date(time):
    """
        Get time and date as separate variables from the time in ISO8601 format
    """
    dateTime = dateutil.parser.parse(time)
    year = dateTime.year
    month = dateTime.month
    day = dateTime.day
    hour = dateTime.hour
    minute = dateTime.minute
    second = dateTime.second

    return (year, month, day, hour, minute, second)

def overlay_to_json(event_id, data_path):
    info_file_path = data_path + event_id + '/current/products/intensity_overlay.pngw'
    with open(info_file_path, 'r') as overlay:
        overlay_file = overlay.readlines()

    overlay_file = list(map(str.strip, overlay_file))
    overlay_file = list(map(float, overlay_file))

    js_file = {
            'dx': overlay_file[0],
            'dy': overlay_file[3],
            'upper_left_x': overlay_file[4],
            'upper_left_y': overlay_file[5]
        }

    with open(data_path + event_id + '/current/products/overlay.json', 'w') as outfile:
            json.dump(js_file, outfile)

    return None

def get_bBox_dict():
    if (os.path.isfile('bBox.txt')):
        with open('bBox.txt') as json_file:
            bBox = json.load(json_file)[0]
        return bBox
    else:
        return False

def get_products_list(event_id, data_path):
    """
        Get the list of products generated for an event and write them to file
    """
    with open('productsDownloadList.json') as json_file:
        productMeta = json.load(json_file)

    products_path = data_path + event_id + '/current/products/'

    fileList = [ item for item in os.listdir(products_path) if os.path.isfile(os.path.join(products_path, item)) ]

    productsList = []

    for product in productMeta:
        if product['name'] in fileList:
            productsList.append(product)


    with open(products_path + 'productList.json', 'w') as outfile:
        json.dump(productsList, outfile)

    return None

def get_parameters (event_id, bBox, data_path):
    """
        Get the event parameters from the info.json file of an event
    """
    info_file_path = data_path + event_id + '/current/products/info.json'
    with open(info_file_path) as f:
        info_file = json.load(f)

    year, month, day, hour, minute, second = separate_time_date(info_file['input']['event_information']['origin_time'])

    parameter_dict = {
            'id': event_id,
            'description': info_file['input']['event_information']['event_description'],
            'day': day,
            'month': month,
            'year': year,
            'hour': hour,
            'minute': minute,
            'second': second,
            'latitude': round(float(info_file['input']['event_information']['latitude']), 2),
            'longitude': round(float(info_file['input']['event_information']['longitude']), 2),
            'magnitude': round(float(info_file['input']['event_information']['magnitude']), 1),
            'depth': round(float(info_file['input']['event_information']['depth']), 1)
            }

    if (bBox == False):
        bBox = {"minLat": -90.0, "maxLat": 90.0, "minLon": -180.0, "maxLon" : 180.0}


    if ( parameter_dict['latitude'] < bBox["minLat"] or parameter_dict['latitude'] > bBox["maxLat"] or
        parameter_dict['longitude'] < bBox["minLon"] or parameter_dict['longitude'] > bBox["maxLon"]):
        return False
    else:
        return parameter_dict

def write_list_to_file(event_list):
    """
        Write event information to file.
    """
    ## This next line is written so the file is saved as a javascript variable
    ## so the ajax call in the website could be avoided
    # with open('events.js.tmp', 'w') as f:
    #     print('var events =', file=f)
    # with open('events.js.tmp', 'a') as outfile:
    #     json.dump(event_list, outfile)
    # shutil.copyfile('events.js.tmp', 'events.js')
    with open('events.json', 'w') as f:
        json.dump(event_list, f, indent = 4)




# not used anymore
def write_version_file():
    yaml_file_path = 'publiccode.yml'
    with open(yaml_file_path, 'r') as yaml:
        yaml_file = yaml.readlines()

    versionElement = [s for s in yaml_file if "softwareVersion" in s][0][:-1]

    versionElement = versionElement.replace('software', 'Website ')

    with open('./scripts/softwareVersion.js', 'w') as f:
        print('var softwareVersion = "<span class=\'go_left\'>' + versionElement +
        '";softwareVersion = softwareVersion + ' +
        '" </span><span class=\'go_right\'>Development of this portal has been made by INGV and it is publicly available at ' +
        '<a href=\'https://github.com/INGV/shakemap4-web\' target=\'_blank\'>GitHub INGV/shakemap4-web  </a></span>";' +
        'document.getElementById("footer_text").innerHTML = softwareVersion;', file=f)

    return

def do_for_all_events(bBox, data_path):
    event_list = []
    folders_list = get_event_ids(data_path)
    events_num = len(folders_list)
    for count, event in enumerate(folders_list, start=1):
        print(str(count) + '/' + str(events_num) + ' - Processing event:' + event)

        ## Try to read the info.json file to put the events in a list for the website to read
        try:
            eventParameters = get_parameters(event, bBox, data_path)
            if (eventParameters != False):
                event_list.append(eventParameters)
        except Exception as e:
            print('Following error occurred for event ' + event + ':')
            print(e)

        ## Try to extract overlay parameters and put them into a json file, so the website can read it
        try:
            overlay_to_json(event, data_path)
        except Exception as e:
            print('No intensity overlay file for event:' + event)
            print(e)

        ## Try to get products list and put them into a json file, so the website can read it
        try:
            get_products_list(event, data_path)
        except Exception as e:
            print('Product file list error for event ' + event + ':')
            print(e)

    write_list_to_file(event_list)
    #write_version_file() Sergio ... not used anymore

# def update_event_list(eventParameters, event_id, eventAction='add'):
#
#     if os.path.isfile('events.json'):
#         with open('events.json') as json_file:
#             events_list = json.load(json_file)
#         if not any(d['id'] == event_id for d in events_list) and eventAction=='add':
#             events_list.append(eventParameters)
#         elif eventAction == 'del':
#             if not any(d['id'] == event_id for d in events_list):
#                 print('Event ' + event_id + ' does not exist in the event list.' )
#             else:
#                 events_list = [x for x in events_list if x['id']!=str(event_id)]
#                 print('Event ' + event_id + ' deleted from event list.')
#         else:
#             events_list = [eventParameters if x['id']==str(event_id) else x for x in events_list]
#     else:
#         if eventAction=='del':
#             print('The event list file does not exist.')
#             return
#         events_list = []
#         events_list.append(eventParameters)
#         print('Nešto ovdje')
#     write_list_to_file(events_list)

def update_event_list(eventParameters, event_id, eventAction='add_or_update'):
    events_list = []
    if os.path.isfile('events.json'):
        with open('events.json') as json_file:
            events_list = json.load(json_file)
    event_index = next((i for i, n in enumerate(events_list) if n['id'] == event_id), None)
    if eventAction=='add_or_update':
        if event_index == None:
            events_list.append(eventParameters)
        else:
            events_list[event_index] = eventParameters
    elif eventAction == 'del':
        if event_index == None:
            print('Event ' + event_id + ' does not exist in the event list.' )
        else:
            events_list.pop(event_index)
            print('Event ' + event_id + ' deleted from event list.')
    write_list_to_file(events_list)

def do_for_one_event(event_id, bBox):
    print('Processing event: ' + event_id)
            ## Try to read the info.json file to put the events in a list for the website to read
    try:
        eventParameters = get_parameters(event_id, bBox, data_path)
        if (eventParameters != False):
            update_event_list(eventParameters, event_id)
    except Exception as e:
        print('Following error occurred for event ' + event_id + ':')
        print(e)

    ## Try to extract overlay parameters and put them into a json file, so the website can read it
    try:
        overlay_to_json(event_id, data_path)
    except Exception as e:
        print('No intensity overlay file for event:' + event_id)
        print(e)

    try:
        get_products_list(event_id, data_path)
    except Exception as e:
        print('Product file list error for event ' + event_id + ':')
        print(e)

def delete_event(event_id, data_path):
    print('Deleting event: ' + event_id)
    try:
        update_event_list(None, event_id, eventAction='del')
    except Exception as e:
        print('Could not delete from list for event' + event_id + ':')
        print(e)

    try:
        shutil.rmtree(data_path + event_id)
        print('Event folder removed from data.')
    except Exception as e:
        print('Could not delete folder for event: ' + event_id + ':')
        print(e)

def get_data_path():
    
    with open('config.js') as configFile:
        configData = configFile.read()
        
    dataPath = configData[configData.find('path:'): configData.rfind('\'')]
    dataPath = dataPath[dataPath.find('\'')+1:]

    return dataPath


def main(event_id, data_path):
    bBox = get_bBox_dict()
    if event_id == False:
        do_for_all_events(bBox, data_path)
    else:
        if os.path.isdir(data_path + event_id):
            do_for_one_event(event_id, bBox)
        else:
            print('Error: event ' + event_id + ' does not exist')
            sys.exit(1)


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument('--eventid', help='Provide the event ID under the script argument --eventid of the event for which the parameters or files have been changed. To run the script for all events do not pass any arguments"')
    parser.add_argument('--deleteid', help='Provide the event ID under the script argument --eventid of the event which you want to delete (from event list and data folder)"')

    args = parser.parse_args()


    data_path = get_data_path()

    if len(sys.argv[:]) < 2:
        print('No event ID has been provided. The script will run for all the events')
        main(False, data_path)
    elif (args.deleteid != None):
        delete_event(args.deleteid, data_path)
    else:
        main(args.eventid, data_path)
