pipeline {
  agent any
  stages {
    stage('Install') {
      steps {
        sh 'pip install -r requirements.txt'
      }
    }
    stage('Check') {
      steps {
        sh 'make test'
      }
    }
  }
}