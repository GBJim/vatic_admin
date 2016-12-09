import os
from subprocess import check_output, call
from flask import Flask, render_template, make_response, request, render_template_string, jsonify, redirect
from scipy.misc import imread
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import uuid
from bbox_comparator import get_alert
from bbox_comparator import parse_txt
import cStringIO
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import requests
from urllib import urlencode
import json




#list_videos_cmd = "docker exec amazing_booth /bin/sh -c 'cd /root/vatic; turkic list'"


def get_videos(user_map):
    return user_map.values()[0].keys()





def get_assignments():
    vatic_path = "/root/vatic"
    inside_cmd = 'cd {}; turkic list'.format(vatic_path)
    cmd = ['docker', 'exec', CONTAINER_NAME, "/bin/bash", '-c', inside_cmd]

    print(" ".join(cmd))

    return check_output(cmd).strip().replace(" ","").split("\n")

def get_urls():
    vatic_path = "/root/vatic"
    inside_cmd = 'cd {}; turkic publish --offline'.format(vatic_path)
    cmd = ['docker', 'exec', CONTAINER_NAME, "/bin/bash", '-c', inside_cmd]
    print(" ".join(cmd))
    return check_output(cmd).strip().split("\n")





#!!!We assume there is only one video name in here!!!
def get_target_links(video_name, frame_num, alert):
    N_segment = frame_num / K_FRAME
    OFFSET_segment = frame_num

    links = []

    #Ignore specific alert isolation_info
    for user in user_map:


        pivot = user_map[user][video_name][N_segment].find("?")
        #print(pivot)
        base_link = "{}/{}".format(VATIC_ADDRESS, user_map[user][video_name][N_segment][pivot:])

        final_link = "{}&frame={}".format(base_link, OFFSET_segment)
        links.append((user, final_link))
    return links











def dump_data(assignments, output_dir="data/query"):

    for assignment in assignments:
        vatic_path = "/root/vatic"
        output_path = "{}/{}.txt".format(output_dir, assignment)
        merge_cmd = "--merge --merge-threshold 0.5"
        inside_cmd = "cd {}; turkic dump {} -o {} {}".format(vatic_path, assignment, output_path, merge_cmd)
        cmd = ['docker', 'exec', CONTAINER_NAME, "/bin/bash", '-c', inside_cmd]
        print(" ".join(cmd))
        call(cmd)


def get_annotation_map(assignments):
    annotation_map = {}

    for assignment in assignments:
        annotation_file = "vatic-docker/data/query/{}.txt".format(assignment)
        pivot = assignment.find("_")
        worker_name = assignment[:pivot]
        video_name = assignment[pivot+1:]
        if video_name not in annotation_map:
            annotation_map[video_name] = {}
        annotation_map[video_name][worker_name] = parse_txt(annotation_file)

    return annotation_map

def get_alerts(annotation_map):
    alerts = {}
    for video_name in annotation_map:
        alerts[video_name] = get_alert(annotation_map[video_name])
    return alerts



def frame_to_path(video_name, frame_num, img_path="vatic-docker/data/frames_in"):
    dir_A = str(int(frame_num / 10000))
    dir_B = str(int(frame_num / 100))
    path = os.path.join(img_path, video_name,  dir_A, dir_B, "{}.jpg".format(frame_num))
    print(path)
    return path


def visualize_frame(video_name, frame_num, boxes, output_dir="static/images"):
    im_path = frame_to_path(video_name, frame_num)
    img = imread(im_path)
    #output_path = os.path.join(output_dir, "999.jpg")
    fig, ax = plt.subplots(1)
    plt.imshow(img)
    #plt.show()

    for box in boxes:
        x1 = box["xmin"]
        y1 = box["ymin"]
        width = box["xmax"] - x1
        length = box["ymax"] - y1
        label = box["source"]
        color = color_map[box["source"]]
        rectangle = plt.Rectangle((x1,y1), width,length, fill=False, edgecolor=color, linewidth=1)
        ax.add_patch(rectangle)
        ax.text(x1, y1 - 2, label,
                bbox=dict(facecolor=color, alpha=0.5),
                fontsize=6, color='white')


    plt.axis("off")
    #plt.show()

    buf = cStringIO.StringIO()
    plt.savefig(buf, bbox_inches='tight',pad_inches=0)
    img = buf.getvalue()
    #plt.savefig(output_path)
    return img


def get_color_map(workers):
    colors = ["r", "g", "b", "y", "w", "p", "o"]
    color_map = {}

    for i, worker in enumerate(sorted(workers)):
        color_map[worker] = colors[i]

    return color_map



def get_alert_boxes(video_name, frame_num):

    alert_boxes = []
    if frame_num in alerts[video_name]:
        isolation_info = alerts[video_name][frame_num]["isolation"]
    else:
        return []

    for worker, worker_isolation_info  in isolation_info.items():
        for objID, bad_matchings in worker_isolation_info.items():
            alert_box = annotation_map[video_name][worker][frame_num][objID].copy()

            alert_box["source"] = worker
            alert_box["id"] = objID
            alert_box["bad_matchings"] = bad_matchings


            alert_boxes.append(alert_box)
    return alert_boxes




def get_img_url(video_name, frame_num, base_url = "/image"):
    return "{}?video_name={}&frame_num={}".format(base_url, video_name, frame_num)



app = Flask(__name__)

@app.route('/image')
def serve_image():
    #return "YoYO!"
    if request.method == 'GET':
        video_name = request.args['video_name']
        frame_num = int(request.args['frame_num'])

        boxes = get_alert_boxes(video_name, frame_num)

        img = visualize_frame(video_name, frame_num, boxes)
        response = make_response(img)
        response.content_type = "image/jpeg"
        return response
    else:
        return "Something is wrong ;)"


def get_next_alert_frame(video_name, old_frame):
    next_frame = float("inf")
    for frame in alerts[video_name]:
        if frame > old_frame and frame < next_frame:
            next_frame = frame
    if next_frame == float("inf"):
        next_frame = old_frame

    return next_frame


def get_previous_alert_frame(video_name, old_frame):
    previous_frame = 0
    for frame in alerts[video_name]:
        if frame < old_frame and frame > previous_frame:
            previous_frame = frame
    if previous_frame == float("inf"):
        previous_frame = old_frame

    return previous_frame


def get_first_alert_frame(video_name):
    target_frames = alerts[video_name].keys()
    if len(target_frames):
        return min(target_frames)
    else:
        return 0




@app.route('/previous')
def previous_alert():
    if request.method == 'GET':
        video_name = request.args['video']
        current_frame = int(request.args['frame'])
        previous_frame = get_previous_alert_frame(video_name, current_frame)


        img_url = get_img_url(video_name, previous_frame)
        #dom = " <img  id='alert-img' frame-num={{frame_num}} src={{img_url}}>"
        alert=alerts[video_name].get(previous_frame ,[])
        target_links = get_target_links(video_name, previous_frame, alert)



        #response = render_template_string(dom, frame_num=frame_num, img_url=img_url)
        #response = {"img_url": img_url, "frame_num": next_frame}
    return jsonify(img_url=img_url, frame_num=previous_frame, alert=alert, target_links=target_links)






@app.route('/next')
def next_alert():
    if request.method == 'GET':
        video_name = request.args['video']
        print(video_name)
        current_frame = int(request.args['frame'])
        next_frame = get_next_alert_frame(video_name, current_frame)


        img_url = get_img_url(video_name, next_frame)
        #dom = " <img  id='alert-img' frame-num={{frame_num}} src={{img_url}}>"
        alert=alerts[video_name].get(next_frame ,[])
        target_links = get_target_links(video_name, next_frame, alert)


        #response = render_template_string(dom, frame_num=frame_num, img_url=img_url)
        #response = {"img_url": img_url, "frame_num": next_frame}
    return jsonify(img_url=img_url, frame_num=next_frame, alert= alert, target_links=target_links)

@app.route('/update')
def update():
    dump_data(assignments)
    global annotation_map
    global alerts
    annotation_map = get_annotation_map(assignments)
    alerts = get_alerts(annotation_map)
    return redirect("./")


@app.route('/')
def index():
    videos = get_videos(user_map)

    if "video_name" in request.args:
        video_name = request.args['video_name']
        videos.remove(video_name)
        videos.insert(0, video_name)


    else:
        video_name = videos[0]

    frame_num = get_first_alert_frame(video_name)
    img_url = get_img_url(video_name, frame_num)
    print(img_url)
    alert = alerts[video_name].get(frame_num, [])
    target_links = get_target_links(video_name, frame_num, alert)


    return render_template('index.html', alerts=alerts, img_url=img_url, videos=videos,frame_num=frame_num,\
        target_links=target_links, alert=alert)



def get_assignments(user_map):
    assignments = []
    for user in user_map:
        for video in user_map[user]:
            assignment = "{}_{}".format(user, video)
            assignments.append(assignment)
    return assignments

if __name__ == "__main__":
    CONTAINER_NAME = "angry_hawking"
    K_FRAME = 322
    VATIC_ADDRESS = "http://172.16.22.51:8892"

    vatic_path = "/root/vatic"
    inside_cmd = 'cd {}; turkic list --detail'.format(vatic_path)
    cmd = ['docker', 'exec', CONTAINER_NAME, "/bin/bash", '-c', inside_cmd]

    print(" ".join(cmd))
    call(cmd)
    user_map = json.load(open("vatic-docker/data/user_map.json"))

    assignments = get_assignments(user_map)
    dump_data(assignments)

    annotation_map = get_annotation_map(assignments)
    alerts = get_alerts(annotation_map)


    workers = user_map.keys()
    color_map = get_color_map(workers)


    #user_map = get_user_map()



    app.run(host='0.0.0.0',debug=True,threaded=True)
