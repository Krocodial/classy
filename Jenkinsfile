
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

def templateName = 'classy-bc'

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
	}// end of stage
	stage('cleanup') {
		steps {
			script {
				openshift.withCluster() {
					openshift.withProject() {
						openshift.selector('all', [ template : templateName ]).delete()
						if (openshift.selector('secrets', templateName).exists()) {
							openshift.selector('secrets', templateName).delete()
						}
					}
				}
			}
		}
	} end of stage
	stage('build') {
		steps {
			script {
				openshift.withCluster() {
					openshift.withProject() {
						def builds = openshift.selector('bc', templateName).related('builds')
						timeout(5) {
							builds.untilEach(1) {
								return (it.object().status.phase == "Complete")
							}
						}
					}
				}
			}
		}
	}// end of stage
  }//end of stages
}//pipeline end


		  
