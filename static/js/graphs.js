document.addEventListener("DOMContentLoaded", (event) => {
    const configsysusage = {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: "CPU%",
                    backgroundColor: 'rgb(138,255,99)',
                    borderColor: 'rgba(138,255,99,0.5)',
                    data: [],
                    fill: false,
                },
                {
                    label: "MEM%",
                    backgroundColor: 'rgb(124,255,222)',
                    borderColor: 'rgba(124,255,222,0.5)',
                    data: [],
                    fill: false,
                }],
        },
        options: {
            maintainAspectRation: false,
            responsive: true,
            title: {
                display: true,
                text: 'System Graphs'
            },
            tooltips: {
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'nearest',
                intersect: true
            },
            scales: {
                xAxes: [{
                    display: true,
                    scaleLabel: {
                        display: false,
                        labelString: 'Time'
                    }
                }],
                yAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Value'
                    }
                }]
            }
        }
    };

    const configcpugraph = {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: "Current Freq.",
                    backgroundColor: 'rgb(138,255,99)',
                    borderColor: 'rgba(138,255,99,0.5)',
                    data: [],
                    fill: false,
                },
                {
                    label: "Min Freq.",
                    backgroundColor: 'rgb(124,255,222)',
                    borderColor: 'rgba(124,255,222,0.5)',
                    data: [],
                    fill: false,
                },
                {
                    label: "Max Freq.",
                    backgroundColor: 'rgb(255,255,255)',
                    borderColor: 'rgb(173,173,173)',
                    data: [],
                    fill: false,
                }],
        },
        options: {
            maintainAspectRation: false,
            responsive: true,
            title: {
                display: true,
                text: 'System Graphs'
            },
            tooltips: {
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'nearest',
                intersect: true
            },
            scales: {
                xAxes: [{
                    display: true,
                    scaleLabel: {
                        display: false,
                        labelString: 'Time'
                    }
                }],
                yAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Value'
                    }
                }]
            }
        }
    };

    const syscontext = document.getElementById('memcpugraph').getContext('2d');
    const cpucontext = document.getElementById('cpufreqgraph').getContext('2d');

    const sysLineChart = new Chart(syscontext, configsysusage);
    const cpuLineChart = new Chart(cpucontext, configcpugraph);

    const source = new EventSource("/chart-data");

    const uptimeText = document.getElementById('valUptime');
    const LoadAvgText = document.getElementById('valLoadAvg');
    const NumPidsText = document.getElementById('valNumPids');
    const PckRcvdText = document.getElementById('valPckRcvd');
    const PckSentText = document.getElementById('valPckSent');
    const NetRcvdText = document.getElementById('valNetRcvd');
    const NetSentText = document.getElementById('valNetSent');

    source.onmessage = function (event) {
        const data = JSON.parse(event.data);
        if (configsysusage.data.labels.length === 20) {
            configsysusage.data.labels.shift();
            configsysusage.data.datasets[0].data.shift();
        }
        configsysusage.data.labels.push(data.time);
        configsysusage.data.datasets[0].data.push(data.cpu_pct);
        configsysusage.data.datasets[1].data.push(data.mem_pct);
        sysLineChart.update();
        if (configcpugraph.data.labels.length === 20) {
            configcpugraph.data.labels.shift();
            configcpugraph.data.datasets[0].data.shift();
        }
        configcpugraph.data.labels.push(data.time);
        configcpugraph.data.datasets[0].data.push(data.cpu_freq_cur);
        configcpugraph.data.datasets[1].data.push(data.cpu_freq_min);
        configcpugraph.data.datasets[2].data.push(data.cpu_freq_max);
        cpuLineChart.update();
        uptimeText.innerText = data.uptime;
        LoadAvgText.innerText = data.load_avg;
        NumPidsText.innerText = data.num_pids;
        PckRcvdText.innerText = data.net_packets_rcvd;
        PckSentText.innerText = data.net_packets_sent;
        NetRcvdText.innerText = data.net_rcvd;
        NetSentText.innerText = data.net_sent;

    }
});