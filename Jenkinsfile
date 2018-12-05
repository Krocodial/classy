node {

	
    stage('checkout for static code analysis') {
        echo "checking out source"
        echo "Build: ${BUILD_ID}"
        checkout scm
    }

    stage('code quality check') {
	
        SONAR_LOGIN = sh (
            script: 'oc env dc/sonarqube --list | awk  -F  "=" \'/SONAR_LOGIN/{print $2}\'',
            returnStdout: true
        ).trim()
        echo "SONAR_LOGIN: ${SONAR_LOGIN}"

		
        SONAR_HOST = sh (
            script: 'oc env dc/sonarqube --list | awk  -F  "=" \'/SONAR_HOST/{print $2}\'',
            returnStdout: true
        ).trim()
        echo "SONAR_HOST: ${SONAR_HOST}"

		
        sh returnStdout: true, 
		script: "chmod +x sonar-runner/bin/sonar-scanner && ./sonar-runner/bin/sonar-scanner -Dsonar.projectKey=classy -Dsonar.sources=. \
			-Dsonar.host.url=${SONAR_HOST} \
			-Dsonar.login=${SONAR_LOGIN}"
        
    }

}
