
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
						if (openshift.selector("secrets", "classy").exists()) {
							openshift.selector("secrets", "classy").delete()
						}
					}
				}
			}
		}
	}// end of stage
	stage('cleanup tools') {
		steps {
			script {
				openshift.withCluster() {
					openshift.withProject() {
						echo "Destroying backend objects..."
						openshift.selector("all", [ template : backendBcTag ]).delete()
						openshift.selector("all", [ template : databaseBcTag ]).delete()
					}
				}
			}
		}
	}// end of stage
	stage('Prepare build configs') {
		steps {
			script {
				openshift.withCluster() {
					openshift.withProject() {
						
						backend = openshift.process(
							readFile(file:"${backendBC}"),
							"-p", 
							"APP_NAME=${APP_NAME}", 
							"NAME_SUFFIX=${DEV_SUFFIX}-${PR_NUM}", 
							"ENV_NAME=${DEV_SUFFIX}", 
							"APP_IMAGE_TAG=${PR_NUM}", 
							"SOURCE_REPOSITORY_URL=${GIT_REPOSITORY}", "SOURCE_REPOSITORY_REF=${GIT_REF}")
							
						database = openshift.process(
							readFile(file:"${databaseBC}"),
								"-p",
								"ENV_NAME=${DEV_SUFFIX}")
							
						openshift.apply(backend)
						openshift.apply(database)
							

						
					}
				}
			}
		}
	}
	stage('building in dev') {
		steps {
			script {
				openshift.withCluster() {
					openshift.withProject() {
						
						def builds = openshift.selector("bc",
							"${APP_NAME}-${DEV_SUFFIX}-${PR_NUM}")
						builds.startBuild("--wait", "--env=ENABLE_DATA_ENTRY=True").logs("f")

							
					}
				}
			}
		}
	}// end of stage
	/*stage('deploy to dev') {
		steps {
			script {
				openshift.withCluster() {
					openshift.withProject(DEV_PROJECT) {
						backend = openshift.process(
							readFile(file:"${backendDC}"),
							"-p", 
							"APP_NAME=${APP_NAME}", 
							"NAME_SUFFIX=${DEV_SUFFIX}-${PR_NUM}", 
							"ENV_NAME=${DEV_SUFFIX}", 
							"APP_IMAGE_TAG=${PR_NUM}", 
							"SOURCE_REPOSITORY_URL=${GIT_REPOSITORY}", "SOURCE_REPOSITORY_REF=${GIT_REF}")
						
						
						database = openshift.process(
							readFile(file:"${databaseDC}"),
							"-p", 
							"APP_NAME=${APP_NAME}", 
							"NAME_SUFFIX=${DEV_SUFFIX}-${PR_NUM}", 
							"ENV_NAME=${DEV_SUFFIX}", 
							"APP_IMAGE_TAG=${PR_NUM}", 
							"SOURCE_REPOSITORY_URL=${GIT_REPOSITORY}", "SOURCE_REPOSITORY_REF=${GIT_REF}")
						
						openshift.apply(database).label(['app':"classy-${DEV_SUFFIX}-${PR_NUM}", 'app-name':"${APP_NAME}", 'env-name':"${DEV_SUFFIX}"], "--overwrite")
							

							
						//for ( o in database ) {
						//	echo "Creating: ${o.metadata.name}-${o.kind}"
						//	openshift.create(o)
						//}
						//for ( o in backend ) {
						//	echo "Creating: ${o.metadata.name}-${o.kind}"
						//	openshift.create(o)
						//}
					}
				}
			}
		}
	}// end of stage
	*/
	stage('tag') {
		steps {
			script {
				openshift.withCluster() {
					openshift.withProject(DEV_PROJECT) {
							
					}
				}
			}
		}
	}//end of stage
  }//end of stages
}//pipeline end


		  
