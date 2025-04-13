<template>
    <div class="mt-4">
      <h5>Características recentes</h5>
      <div v-if="caracteristicas">
        <ul class="list-group">
          <li class="list-group-item" v-for="(dados, tipo) in caracteristicas" :key="tipo">
            <strong>{{ tipo }}</strong>: {{ dados?.valor ?? 'Sem dado' }} <span v-if="dados">({{ dados.data }})</span>
          </li>
        </ul>
  
        <button class="btn btn-outline-secondary mt-3" @click="exportarCSV">Exportar CSV</button>
      </div>
      <div v-else>Carregando...</div>
    </div>
  </template>
  
  <script>
  import axios from 'axios'
  
  export default {
    props: ['cpf'],
    data() {
      return {
        caracteristicas: null
      }
    },
    async mounted() {
      const res = await axios.get(`https://desafio-anlix-api.up.railway.app/pacientes/${this.cpf}/caracteristicas`)
      this.caracteristicas = res.data
    },
    methods: {
      exportarCSV() {
        window.open(`https://desafio-anlix-api.up.railway.app/export?cpfs=${this.cpf}`, '_blank')
      }
    }
  }
  </script>