<template>
    <div>
      <div class="input-group mb-3">
        <input v-model="busca" @keyup.enter="buscar" placeholder="Digite o nome do paciente" class="form-control" />
        <button class="btn btn-primary" @click="buscar">Buscar</button>
      </div>
  
      <ul class="list-group" v-if="resultados.length">
        <li v-for="p in resultados" :key="p.cpf" class="list-group-item d-flex justify-content-between">
          {{ p.nome }}
          <button class="btn btn-sm btn-outline-success" @click="$emit('pacienteSelecionado', p)">Selecionar</button>
        </li>
      </ul>
    </div>
  </template>
  
  <script>
  import axios from 'axios'
  
  export default {
    data() {
      return {
        busca: '',
        resultados: []
      }
    },
    methods: {
      async buscar() {
        if (!this.busca.trim()) return
        try {
          const res = await axios.get(`https://desafio-anlix-api.up.railway.app/pacientes?nome=${this.busca}`)
          this.resultados = res.data
        } catch (err) {
          console.error('Erro na busca:', err)
          this.resultados = []
        }
      }
    }
  }
  </script>