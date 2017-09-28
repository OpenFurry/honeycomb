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
        sh '''source venv/bin/activate
make test-travis
deactivate'''
      }
    }
  }
}