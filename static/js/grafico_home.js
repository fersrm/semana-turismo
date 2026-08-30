const chartContainer = document.getElementById("chart_home");
const chartDataElement = document.getElementById("grafico-semana-data");

if (chartContainer && chartDataElement && window.echarts) {
  const chartData = JSON.parse(chartDataElement.textContent);

  const myChart = echarts.init(chartContainer);

  const option = {
    backgroundColor: "transparent",

    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "shadow",
      },
      formatter(params) {
        const item = params[0];

        return `
          <strong>${item.axisValue}</strong><br>
          Participantes: ${item.value}
        `;
      },
    },

    grid: {
      left: "5%",
      right: "5%",
      bottom: "10%",
      top: "16%",
      containLabel: true,
    },

    xAxis: {
      type: "category",
      data: chartData.labels,
      axisTick: {
        alignWithLabel: true,
      },
      axisLine: {
        lineStyle: {
          color: "#6b7280",
        },
      },
      axisLabel: {
        color: "#e5e7eb",
        fontWeight: "bold",
      },
    },

    yAxis: {
      type: "value",
      minInterval: 1,
      name: "Participantes",
      nameTextStyle: {
        color: "#e5e7eb",
        fontWeight: "bold",
      },
      axisLine: {
        show: true,
        lineStyle: {
          color: "#6b7280",
        },
      },
      splitLine: {
        lineStyle: {
          color: "rgba(255, 255, 255, 0.10)",
        },
      },
      axisLabel: {
        color: "#e5e7eb",
      },
    },

    series: [
      {
        name: "Participantes",
        type: "bar",
        data: chartData.values,
        barMaxWidth: 55,
        itemStyle: {
          color: "#10b981",
          borderRadius: [8, 8, 0, 0],
        },
        label: {
          show: true,
          position: "top",
          color: "#ffffff",
          fontWeight: "bold",
        },
      },
    ],
  };

  myChart.setOption(option);

  window.addEventListener("resize", () => {
    myChart.resize();
  });
}
