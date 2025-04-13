<!-- src/App.vue -->
<template>
  <div class="container py-4">
    <h2 class="mb-4">Painel de Pacientes - Desafio Anlix</h2>

    <PacienteBusca @pacienteSelecionado="handlePacienteSelecionado" />

    <div v-if="paciente">
      <CaracteristicasResumo :cpf="paciente.cpf" />

      <hr />

      <div class="mb-3">
        <label>Selecione a característica para o gráfico:</label>
        <select v-model="caracteristicaSelecionada" class="form-select w-auto">
          <option value="ind_card">Índice Cardíaco</option>
          <option value="ind_pulm">Índice Pulmonar</option>
        </select>
      </div>

      <GraficoTemporal
        v-if="caracteristicaSelecionada"
        :cpf="paciente.cpf"
        :tipo="caracteristicaSelecionada"
      />
    </div>
  </div>
</template>

<script>
import PacienteBusca from './components/PacienteBusca.vue'
import CaracteristicasResumo from './components/CaracteristicasResumo.vue'
import GraficoTemporal from './components/GraficoTemporal.vue'

export default {
  components: {
    PacienteBusca,
    CaracteristicasResumo,
    GraficoTemporal
  },
  data() {
    return {
      paciente: null,
      caracteristicaSelecionada: 'ind_card'
    }
  },
  methods: {
    handlePacienteSelecionado(paciente) {
      this.paciente = paciente
    }
  }
}
</script>
