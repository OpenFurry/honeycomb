pipeline {
  agent any
  stages {
    stage('Install') {
      steps {
        sh '''make venv
pip install -r requirements.txt'''
      }
    }
    stage('Check') {
      steps {
        sh 'make test'
      }
    }
  }
}