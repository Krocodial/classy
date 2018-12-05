node {
	
    stage('checkout for static code analysis') {
        echo "checking out source"
        echo "Build: ${BUILD_ID}"
        checkout scm
    }

    stage('code quality check') {
		
	
	
        SONARQUBE_PWD = sh (
            script: 'oc env dc/sonarqube --list | awk  -F  "=" \'/SONARQUBE_ADMINPW/{print $2}\'',
            returnStdout: true
        ).trim()
        echo "SONARQUBE_PWD: ${SONARQUBE_PWD}"

        SONARQUBE_URL = sh (
            script: 'oc get routes -o wide --no-headers | awk \'/sonarqube/{ print match($0,/edge/) ?  "https://"$2 : "http://"$2 }\'',
            returnStdout: true
        ).trim()
        echo "SONARQUBE_URL: ${SONARQUBE_URL}"

        dir('sonar-runner') {
            sh returnStdout: true, 
			script: "chmod +x bin/sonar-scanner && ./bin/sonar-scanner   -Dsonar.projectKey=classy -Dsonar.sources=. \
				-Dsonar.host.url=https://sonarqube-l9fjgg-tools.pathfinder.gov.bc.ca \
				-Dsonar.login=b9d3a63268e3e729686f1afc9ff8bdb30e8be941"
        }
    }
	
	stage('validation') {
        dir('navunit') {
            sh './gradlew --debug --stacktrace phantomJsTest'
        }
    }

	
    
}