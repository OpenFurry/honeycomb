pipeline {
  agent any
  stages {
    stage('Install') {
      steps {
        sh 'make deps'
      }
    }
    stage('Test') {
      steps {
        sh 'make test'
      }
    }
  }
}