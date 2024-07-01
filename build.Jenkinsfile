pipeline {
    agent any
    options {
        buildDiscarder(logRotator(daysToKeepStr: '30'))
        disableConcurrentBuilds()
        timestamps()
    }

    environment {
        DOCKER_REPO = 'ofriz/jenkinsproject'
    }
    stages {
        stage('Checkout') {
            steps {
                // Checkout code
                checkout scm
            }
        }
        stage('Build, tag, and push docker image') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                    script {
                        // Extract Git commit hash
                        bat(script: 'git rev-parse --short HEAD > gitCommit.txt')
                        def gitCommit = readFile('gitCommit.txt').trim()

                        // Define semver
                        def semver = "1.0.${BUILD_NUMBER}" // Example semver

                        // Tag with semver, git commit, and latest
                        def semverTag = "${semver}"
                        def gitTag = "${gitCommit}"
                        def latestTag = "latest"

                        // Build and tag Docker images
                        bat """
                            cd polybot
                            docker login -u ${USER} -p ${PASS}
                            docker build -t %DOCKER_REPO%:${semverTag} -t %DOCKER_REPO%:${gitTag} -t %DOCKER_REPO%:${latestTag} .
                            docker push %DOCKER_REPO%:${semverTag}
                            docker push %DOCKER_REPO%:${gitTag}
                            docker push %DOCKER_REPO%:${latestTag}
                        """
                    }
                }
            }
        }
    }
    post {
        always {
            script {
                // Remove dangling images
                bat '''
                    FOR /F "tokens=*" %i IN ('docker images -f "dangling=true" -q') DO (
                        docker rmi %i
                    )
                '''

                // Remove specific repository images
                bat '''
                    FOR /F "tokens=*" %i IN ('docker images ${env.DOCKER_REPO} -q') DO (
                        docker rmi %i
                    )
                '''
            }
        }
    }
}