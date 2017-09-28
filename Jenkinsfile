pipeline {
  agent any
  stages {
    stage('Install') {
      steps {
        sh 'make clean deps'
      }
    }
    stage('Test') {
      steps {
        sh 'make test-travis'
      }
    }
  }
}