pipeline {
  agent any
  stages {
    stage('Check') {
      steps {
        parallel(
          "Check": {
            sh 'make test'
            
          },
          "Install": {
            sh 'make deps'
            
          }
        )
      }
    }
  }
}