<template>
    <div class="mt-5">
      <h5>Gráfico temporal - {{ tipo }}</h5>
      <div class="mb-2">
        <label>De:</label>
        <input type="date" v-model="de" class="form-control" />
        <label class="mt-2">Até:</label>
        <input type="date" v-model="ate" class="form-control" />
      </div>
  
      <button class="btn btn-primary my-2" @click="buscarDados">Atualizar gráfico</button>
      <canvas ref="graficoCanvas"></canvas>
    </div>
  </template>
  
  <script>
  import axios from 'axios'
  import { Chart, registerables } from 'chart.js'
  Chart.register(...registerables)
  
  export default {
    props: ['cpf', 'tipo'],
    data() {
      return {
        de: '',
        ate: '',
        chart: null
      }
    },
    methods: {
      async buscarDados() {
        if (!this.de || !this.ate) return
  
        const res = await axios.get(`https://desafio-anlix-api.up.railway.app/pacientes/${this.cpf}/caracteristicas/${this.tipo}?de=${this.de}&ate=${this.ate}`)
  
        const labels = res.data.map(m => m.data)
        const valores = res.data.map(m => m.valor)
  
        if (this.chart) this.chart.destroy()
  
        this.chart = new Chart(this.$refs.graficoCanvas, {
          type: 'line',
          data: {
            labels,
            datasets: [{
              label: this.tipo,
              data: valores,
              borderColor: 'blue',
              fill: false
            }]
          },
          options: {
            responsive: true,
            plugins: {
              legend: { display: false }
            }
          }
        })
      }
    }
  }
  </script>
  