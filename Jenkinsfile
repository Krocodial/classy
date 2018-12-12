
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

pipeline {
  environment {
  
	APP_NAME = 'classy'
	REPOSITORY = 'https://github.com/Krocodial/classy.git'
	
	TOOLS_PROJECT = 'l9fjgg-tools'
	
	DEV_PROJECT = 'l9fjgg-dev'
	DEV_SUFFIX = 'dev'
	DEV_HOST = 'classy-dev.pathfinder.gov.bc.ca'
  
  
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
	
	PR_NUM = "${env.JOB_BASE_NAME}".toLowerCase()
  
	
  
  }
  agent any
  options {
	timeout(time: 20, unit: 'MINUTES')
  }
  stages {
    stage('preamble') {
		steps {
			script {
				openshift.withCluster() {
					openshift.withProject() {
						echo "Using project: ${openshift.project()}"
					}
				}
			}
		}
	}
	
	
	
	
	/*stage('Prepare Templates') {
		steps {
			script {
				echo "Cancelling prev builds"
				timeout(10) {
					openshift.process("cancel-build",
						"*"
					)
				}
				echo "previous builds cancelled"
	
				/*echo "processing build templates"
				def dbtemplate = openshift.process("-f", 
					"openshift/postgresql.bc.json",
					"ENV_NAME=${DEV_SUFFIX}"
				)*/
					
				def buildtemplate = openshift.process("-f",
					"openshift/backend.bc.json",
					"ENV_NAME=${DEV_SUFFIX}",
					"NAME_SUFFIX=-${DEV_SUFFIX}-${PR_NUM}",
					"APP_IMAGE_TAG=${PR_NUM}",
					"SOURCE_REPOSITORY_URL=${REPOSITORY}",
					"SOURCE_REPOSITORY_REF=openshift"
				)
	
		}//script end
	  }//steps end
	}//stage end*/
  }//end of stages
}//pipeline end

/*stage('SonarQube analysis') {
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
		  }//podTemplate end*/