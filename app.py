from flask import Flask, render_template, Response, stream_with_context
import shutil
import psutil
import time
import datetime
import os
import json
import pathlib


app = Flask(__name__)

def check_config():
    sample_config = {
        'port': 5555,
        'storage_mounts': [{'name': 'root', 'mountpoint': '/'}]
    }
    if not os.path.exists('config.json'):
        with open("config.json", "w") as f:
            f.write(json.dumps(sample_config))
            f.close()
            print("A new config file has been created. Please modify json.config to your own needs.")
            sysinfo_config = sample_config
    else:
        with open("config.json", "r") as f:
            sysinfo_config = json.load(f)

    return sysinfo_config

def humanbytes(totalbytes):
    """Return the given bytes as a human friendly KB, MB, GB, or TB string."""
    totalbytes = float(totalbytes)
    kbytes = float(1024)
    mbytes = float(kbytes ** 2)  # 1,048,576
    gbytes = float(kbytes ** 3)  # 1,073,741,824
    tbytes = float(kbytes ** 4)  # 1,099,511,627,776

    if totalbytes < kbytes:
        return '{0} {1}'.format(totalbytes, 'Bytes' if 0 == totalbytes > 1 else 'Byte')
    elif totalbytes <= kbytes < mbytes:
        return '{0:.2f} KB'.format(totalbytes / tbytes)
    elif mbytes <= totalbytes < gbytes:
        return '{0:.2f} MB'.format(totalbytes / mbytes)
    elif gbytes <= totalbytes < tbytes:
        return '{0:.2f} GB'.format(totalbytes / gbytes)
    elif tbytes <= totalbytes:
        return '{0:.2f} TB'.format(totalbytes / tbytes)


def get_diskinfo():
    # Total = 0, Used = 1, Free = 2
    # disk_usg = shutil.disk_usage('/')
    # in_use_pct = round(100 * float(disk_usg[1]) / float(disk_usg[0]), 2)
    disks = []
    # disk = {
    #     'name': '/',
    #     'total': humanbytes(disk_usg[0]),
    #     'used': humanbytes(disk_usg[1]),
    #     'free': humanbytes(disk_usg[2]),
    #     'in_use_pct': in_use_pct
    # }

    for mount in sysinfo_config['storage_mounts']:
        in_use_pct = round(100 * float(shutil.disk_usage(mount['mountpoint'])[1]) /
                           float(shutil.disk_usage(mount['mountpoint'])[0]), 2)
        disk = {
            'name': mount['name'],
            'total': humanbytes(shutil.disk_usage(mount['mountpoint'])[0]),
            'used': humanbytes(shutil.disk_usage(mount['mountpoint'])[1]),
            'free': humanbytes(shutil.disk_usage(mount['mountpoint'])[2]),
            'in_use_pct': in_use_pct
        }
        disks.append(disk)

    return disks


def get_sysinfo():
    uptime_seconds = time.time() - psutil.boot_time()
    # Convert to human-friendly format, chop off microseconds
    uptime_human = str(datetime.timedelta(seconds=uptime_seconds)).split(".")[0]
    system_info = {
        'time': datetime.datetime.now().strftime('%H:%M:%S'),
        'cpu_pct': psutil.cpu_percent(),
        'mem_pct': psutil.virtual_memory()[2],
        'mem_total': humanbytes(psutil.virtual_memory()[0]),
        'mem_avail': humanbytes(psutil.virtual_memory()[1]),
        'mem_free': humanbytes(psutil.virtual_memory()[4]),
        'uptime': uptime_human,
        'cpu_count': psutil.cpu_count(),
        'cpu_freq_cur': psutil.cpu_freq()[0],
        'cpu_freq_min': psutil.cpu_freq()[1],
        'cpu_freq_max': psutil.cpu_freq()[2],
        # Rounding up the averages to 2 digits, because we get a LONG number otherwise
        'load_avg': [round(x, 2) for x in psutil.getloadavg()],
        'num_pids': len(psutil.pids()),
        'net_sent': humanbytes(psutil.net_io_counters()[0]),
        'net_rcvd': humanbytes(psutil.net_io_counters()[1]),
        'net_packets_sent': psutil.net_io_counters()[2],
        'net_packets_rcvd': psutil.net_io_counters()[3],

    }

    return system_info


@app.route("/")
def index():
    context = {
        'hostname': os.uname()[1],
        'storage': get_diskinfo(),
        'sysinfo': get_sysinfo()
    }

    return render_template("index.html", context=context)


@app.route('/chart-data')
def chart_data():
    def get_system_data():
        while True:
            # uptime_seconds = time.time() - psutil.boot_time()
            # Convert to human-friendly format, chop off microseconds
            # uptime_human = str(datetime.timedelta(seconds=uptime_seconds)).split(".")[0]
            system_info = get_sysinfo()
            yield f"data: {json.dumps(system_info)}\n\n"
            time.sleep(1)

    response = Response(stream_with_context(get_system_data()), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response


if __name__ == '__main__':
    sysinfo_config = check_config()
    app.run(threaded=True, debug=False, port=sysinfo_config['port'], host='0.0.0.0')