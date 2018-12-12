
@NonCPS
String getUrlForRoute(String routeName, String projectNameSpace = '') {

  def nameSpaceFlag = ''
  if(projectNameSpace?.trim()) {
    nameSpaceFlag = "-n ${projectNameSpace}"
  }
  
  def url = sh (
    script: "oc get routes ${nameSpaceFlag} -o wide --no-headers | awk \'/${routeName}/{ print match(\$0,/edge/) ?  \"https://\"\$2 : \"http://\"\$2 }\'",
    returnStdout: true
  ).trim()

  return url
}

@NonCPS
String getSonarQubePwd() {

  sonarQubePwd = sh (
    script: 'oc env dc/sonarqube --list | awk  -F  "=" \'/SONARQUBE_ADMINPW/{print $2}\'',
    returnStdout: true
  ).trim()

  return sonarQubePwd
}

// The jenkins-python3nodejs template has been purpose built for supporting SonarQube scanning.
pipeline {
  environment {
	SONAR_ROUTE_NAME = 'sonarqube'
	SONAR_ROUTE_NAMESPACE = 'l9fjgg-tools'
	SONAR_PROJECT_NAME = 'Data Security classification Repository'
	SONAR_PROJECT_KEY = 'classy'
	SONAR_PROJECT_BASE_DIR = '../'
	SONAR_SOURCES = './'
  
	SONARQUBE_URL = sh (
		script: "oc get routes sonarqube -o wide --no-headers | awk \'/sonarqube/ {print \"https://\"\$2}\'",
		returnStdout: true
		)
	
    SONARQUBE_PWD = getSonarQubePwd().trim()
  
  }
  agent any
  stages {
    stage('SonarQube analysis') {
	  steps {
        script {
		  podTemplate(
			label: 'jenkins-python3nodejs',
			  name: 'jenkins-python3nodejs',
			  serviceAccount: 'jenkins',
			  cloud: 'openshift',
			  containers: [
				containerTemplate(
				  name: 'jnlp',
				  image: '172.50.0.2:5000/openshift/jenkins-slave-python3nodejs',
				  resourceRequestCpu: '1000m',
				  resourceLimitCpu: '2000m',
				  resourceRequestMemory: '2Gi',
				  resourceLimitMemory: '4Gi',
				  workingDir: '/tmp',
				  command: '',
				  args: '${computer.jnlpmac} ${computer.name}'
				)
			  ]
		  ){
		    node('jenkins-python3nodejs') {

					checkout scm
					echo "Performing static SonarQube code analysis ..."

					echo "URL: ${SONARQUBE_URL}"
					echo "PWD: ${SONARQUBE_PWD}"

					dir('sonar-runner') {

						sh (
						  returnStdout: true,
						  script: "chmod +x gradlew"
						)
						
						sh (
						  returnStdout: true,
						  script: "./gradlew sonarqube --stacktrace --info \
							-Dsonar.verbose=true \
							-Dsonar.projectName='${SONAR_PROJECT_NAME}' \
							-Dsonar.projectKey=${SONAR_PROJECT_KEY} \
							-Dsonar.projectBaseDir=${SONAR_PROJECT_BASE_DIR} \
							-Dsonar.sources=${SONAR_SOURCES} \
							-Dsonar.host.url=${SONARQUBE_URL}"
						)
					}//sonar-runner end

			}//node end
		  }//podTemplate end
		}//script end
	  }//steps end
	}//stage end
  }//end of stages
}//pipeline end