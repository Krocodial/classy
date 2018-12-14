
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

def backendBC = 'openshift/templates/classy-bc.json'
def databaseBC = 'openshift/templates/postgres-bc.json'

def backendDC = 'openshift/templates/classy-dc.json'
def databaseDC = 'openshift/templates/postgres-dc.json'

def backendBcTag = 'classy-bc'
def backendDcTag = 'classy-dc'
def databaseDcTag = 'postgres-dc'
def databaseBcTag = 'postgres-bc'

pipeline {
  environment {
  
	APP_NAME = 'classy'
	
	GIT_REPOSITORY = 'https://github.com/Krocodial/classy.git'
	GIT_REF = 'openshift'
	
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
	
	PR_NUM = "${BUILD_NUMBER}"
	
  
	
  
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
					openshift.withProject(DEV_PROJECT) {
						echo "Destroying backend objects..."
						//openshift.selector("all", [ template : templateName ]).delete()
						openshift.selector("all", [ template : backendBcTag ]).delete()
						openshift.selector("all", [ template : backendDcTag ]).delete()
						openshift.selector("all", [ template : databaseDcTag ]).delete()
					}
				}
			}
		}
	}// end of stage
	stage('Building') {
		steps {
			script {
				openshift.withCluster() {
					openshift.withProject(DEV_PROJECT) {
						backend = openshift.process(
							readFile(file:"${backendBC}"),
							"-p", 
							"APP_NAME=${APP_NAME}", 
							"NAME_SUFFIX=${DEV_SUFFIX}-${PR_NUM}", 
							"ENV_NAME=${DEV_SUFFIX}", 
							"APP_IMAGE_TAG=${PR_NUM}", 
							"SOURCE_REPOSITORY_URL=${GIT_REPOSITORY}", "SOURCE_REPOSITORY_REF=${GIT_REF}")
							
						def tmp = openshift.selector("pvc", databaseBcTag).describe()
						echo "${tmp}"
						tmp = openshift.selector("pv", databaseBcTag)
						echo "${tmp}"
							
						/*if(!openshift.selector("pvc", databaseBcTag).exists()){
							database = openshift.process(
								readFile(file:"${databaseBC}"),
								"-p", 
								"APP_NAME=${APP_NAME}", 
								"NAME_SUFFIX=${DEV_SUFFIX}-${PR_NUM}", 
								"ENV_NAME=${DEV_SUFFIX}", 
								"APP_IMAGE_TAG=${PR_NUM}", 
								"SOURCE_REPOSITORY_URL=${GIT_REPOSITORY}", "SOURCE_REPOSITORY_REF=${GIT_REF}")
							for ( o in database ) {
								echo "Creating: ${o.metadata.name}-${o.kind}"
								openshift.create(o)
							}
						}*/
						
						for ( o in backend ) {
							echo "Creating: ${o.metadata.name}-${o.kind}"
							openshift.create(o)
						}
					}
				}
			}
		}
	}// end of stage
	/*stage('build') {
		steps {
			script {
				openshift.withCluster() {
					openshift.withProject(DEV_PROJECT) {
						def nb = openshift.newBuild("templatepath", 
							"--APP_NAME=classy", 
							"--NAME_SUFFIX=dev", 
							"--ENV_NAME=dev", 
							"--APP_IMAGE_TAG=latest", 
							"--SOURCE_REPOSITORY_URL=https://github.com/Krocodial/classy.git", "--SOURCE_REPOSITORY_REF=openshift")
						def builds = nb.narrow('bc').related('builds')
						//openshift.selector('bc', templateName).related('builds')
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
	*/
  }//end of stages
}//pipeline end


		  
