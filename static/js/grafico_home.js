const chartContainer = document.getElementById("chart_home");
const chartDataElement = document.getElementById("grafico-semana-data");

if (chartContainer && chartDataElement && window.echarts) {
  const chartData = JSON.parse(chartDataElement.textContent);

  const myChart = echarts.init(chartContainer);

  const hoy = new Date();

  // JS: domingo = 0, lunes = 1, ..., sábado = 6
  const diaActual = hoy.getDay();

  // Lo convertimos al índice de tu gráfico:
  // lunes = 0, martes = 1, ..., viernes = 4
  const indiceHoy = diaActual >= 1 && diaActual <= 5 ? diaActual - 1 : -1;

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
          color(params) {
            // Hoy en naranja, resto verde
            return params.dataIndex === indiceHoy ? "#f59e0b" : "#10b981";
          },

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
