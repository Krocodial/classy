

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
def nginxBC = 'openshift/templates/nginx-bc.json'

def backendDC = 'openshift/templates/classy-dc.json'
def databaseDC = 'openshift/templates/postgres-dc.json'
def nginxDC = 'openshift/templates/nginx-dc.json'

def backendBcTag = 'classy-bc'
def backendDcTag = 'classy-dc'
def databaseDcTag = 'postgres-dc'
def databaseBcTag = 'postgres-bc'
def nginxBcTag = 'nginx-bc'
def nginxDcTag = 'nginx-dc'

def appName = 'classy'

pipeline {
  environment {
  
	APP_NAME = 'classy'
	
	GIT_REPOSITORY = 'https://github.com/Krocodial/classy.git'
	GIT_REF = 'nginx-openshift'
	
	TOOLS_PROJECT = 'l9fjgg-tools'
	
	DEV_PROJECT = 'l9fjgg-dev'
	DEV_SUFFIX = 'dev'
	DEV_HOST = 'classy-dev.pathfinder.gov.bc.ca'
  
	TEST_PROJECT = 'l9fjgg-test'
	TEST_SUFFIX = 'test'
	TEST_HOST = 'classy-test.pathfinder.gov.bc.ca'
  

	SONAR_ROUTE_NAME = 'sonarqube'
	SONAR_ROUTE_NAMESPACE = 'l9fjgg-tools'
	SONAR_PROJECT_NAME = 'Data Security classification Repository'
	SONAR_PROJECT_KEY = 'classy'
	SONAR_PROJECT_BASE_DIR = '../classy/'
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
	stage('preamble & sweeping floor') {
		steps {
			script {
				openshift.withCluster() {
					openshift.withProject() {
						echo "Destroying backend objects..."
						openshift.selector("all", [ template : backendBcTag ]).delete()
						openshift.selector("all", [ template : nginxBcTag ]).delete()
					}
				}
			}
		}
	}// end of stage
	stage('Preparing build configs && building images') {
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
							"SOURCE_REPOSITORY_URL=${GIT_REPOSITORY}", 
							"SOURCE_REPOSITORY_REF=${GIT_REF}")

						openshift.apply(backend)
						
						nginx = openshift.process(
							readFile(file:"${nginxBC}"),
							"-p",
							"APP_NAME=${APP_NAME}",
							"NAME_SUFFIX=${DEV_SUFFIX}-${PR_NUM}",
							"ENV_NAME=${DEV_SUFFIX}", 
							"APP_IMAGE_TAG=${PR_NUM}", 
							"SOURCE_REPOSITORY_URL=${GIT_REPOSITORY}", 
							"SOURCE_REPOSITORY_REF=${GIT_REF}"
							)
							
						openshift.apply(nginx)
						
						echo "select 'bc' ${APP_NAME}-${DEV_SUFFIX}-${PR_NUM} and run startBuild() on them"
						def builds = openshift.selector("bc",
							"${APP_NAME}")
						builds.startBuild("--wait", "--env=ENABLE_DATA_ENTRY=True")

						echo "building nginx bc"
						def nginx = openshift.selector("bc", 
							"proxy-nginx-${PR_NUM}")
						nginx.startBuild("--wait")
						
					}
				}
			}
		}
	}// end of stage
	stage('sonar scanner') {
	  steps {
        script {
			openshift.withCluster() {
				openshift.withProject(TOOLS_PROJECT) {
					checkout scm
					echo "Performing static SonarQube code analysis ..."

					echo "URL: ${SONARQUBE_URL}"
					//echo "PWD: ${SONARQUBE_PWD}"

					dir('sonar-runner') {
						sh (
						  returnStdout: true,
						  script: "chmod +x gradlew"
						)
						
						SONAR_OUT = sh (
						  returnStatus: true,
						  //returnStdout: true,
						  script: "./gradlew sonarqube --stacktrace --info \
							-Dsonar.verbose=true \
							-Dsonar.projectName='${SONAR_PROJECT_NAME}' \
							-Dsonar.projectKey=${SONAR_PROJECT_KEY} \
							-Dsonar.projectBaseDir=${SONAR_PROJECT_BASE_DIR} \
							-Dsonar.sources=${SONAR_SOURCES} \
							-Dsonar.host.url=${SONARQUBE_URL}"
						)
						
						echo "${SONAR_OUT}"
					}//sonar-runner end
				}//script end
			}
		}
	  }//steps end
	}// end of stage
	stage('cleaning dev space') {
		steps {
			script {
				openshift.withCluster() {
					openshift.withProject(DEV_PROJECT) {
						echo "Destroying backend objects..."
						openshift.selector("all", [ template : backendBcTag ]).delete()
						openshift.selector("all", [ template : backendDcTag ]).delete()
						openshift.selector("all", [ template : databaseDcTag ]).delete()
						openshift.selector("all", [ template : nginxDcTag ]).delete()
						if (openshift.selector("secrets", "classy-dev").exists()) {
							openshift.selector("secrets", "classy-dev").delete()
						}
					}
				}
			}
		}
	}// end of stage
	
	stage('deploy to dev') {
		steps {
			script {
				openshift.withCluster() {
					openshift.withProject(DEV_PROJECT) {
						input "Ready to promote to DEV?"
						
						//if (openshift.selector("secrets", "classy-dev").exists()) {
						//	openshift.selector("secrets", "classy-dev").delete()
						//}
						/*if (!openshift.selector("pvc", "postgresql").exists()) {
							
							echo "no PVC found, creating..."
						
							databasePVC = openshift.process(
							readFile(file:"${databaseBC}"))
							
							openshift.apply(databasePVC)
						}
						*/
						databasePVC = openshift.process(
							readFile(file:"${databaseBC}"))
							
						openshift.apply(databasePVC)
						
						database = openshift.process(
							readFile(file:"${databaseDC}"),
							"-p", 
							"APP_NAME=${APP_NAME}", 
							"NAME_SUFFIX=${DEV_SUFFIX}-${PR_NUM}", 
							"ENV_NAME=${DEV_SUFFIX}", 
							"APP_IMAGE_TAG=${PR_NUM}", 
							"SOURCE_REPOSITORY_URL=${GIT_REPOSITORY}", 
							"SOURCE_REPOSITORY_REF=${GIT_REF}")
						
						
						backend = openshift.process(
							readFile(file:"${backendDC}"),
							"-p", 
							"APP_NAME=${APP_NAME}", 
							"NAME_SUFFIX=${DEV_SUFFIX}-${PR_NUM}", 
							"ENV_NAME=${DEV_SUFFIX}", 
							"APP_IMAGE_TAG=${PR_NUM}", 
							"SOURCE_REPOSITORY_URL=${GIT_REPOSITORY}", 
							"SOURCE_REPOSITORY_REF=${GIT_REF}")
						
						nginx = openshift.process(
							readFile(file:"${nginxDC}"),
							"-p",
							"APP_NAME=${APP_NAME}", 
							"NAME_SUFFIX=${DEV_SUFFIX}-${PR_NUM}", 
							"ENV_NAME=${DEV_SUFFIX}", 
							"APP_IMAGE_TAG=${PR_NUM}",
							"APPLICATION_DOMAIN=${APP_NAME}-${DEV_SUFFIX}.pathfinder.gov.bc.ca")
						
						
						openshift.apply(database)
							.label(['app':"classy-${DEV_SUFFIX}", 
							'app-name':"${APP_NAME}", 
							'env-name':"${DEV_SUFFIX}"], 
							"--overwrite")
						
						openshift.apply(backend)
							.label(['app':"classy-${DEV_SUFFIX}", 
							'app-name':"${APP_NAME}", 
							'env-name':"${DEV_SUFFIX}"], 
							"--overwrite")

						openshift.apply(nginx)
							.label(['app':"classy-${DEV_SUFFIX}", 
							'app-name':"${APP_NAME}", 
							'env-name':"${DEV_SUFFIX}"], 
							"--overwrite")
		

					}
				}
			}
		}
	}// end of stage
	stage('Promoting images to dev') {
		steps {
			script {
				openshift.withCluster() {
					openshift.withProject(DEV_PROJECT) {
					
						openshift.tag("${TOOLS_PROJECT}/classy:${PR_NUM}",
							"${DEV_PROJECT}/classy:dev")
							
						openshift.tag("${TOOLS_PROJECT}/proxy-nginx:${PR_NUM}",
							"${DEV_PROJECT}/proxy-nginx-${DEV_SUFFIX}:dev")
							
						def dcs = openshift.selector("dc", [ app : 'classy' ])
						dcs.rollout().status()
							
						//def dc = openshift.selector('dc', 'postgresql')
						//dc.rollout().status()
					}
				}
			}
		}
	}// end of stage

	/*stage('Integrations tests') {
		steps {
			script {
				openshift.withCluster() {
					//input "Ready to promote to TEST?"
					
					//user_input = input(
					//	id: 'Proceed-tools', message: 'Proceed to test?', parameters: [
					//		[$class: 'BooleanParameterDefinition', defaultValue: true, description: '', //name: 'Please confirm you wish to proceed to test']
					//		])
					//echo "${user_input}"
				}
			}
		}
	}// end of stage
	stage('Deploy to TEST') {
		steps {
			script {
				openshift.withCluster() {
					openshift.withProject(TEST_PROJECT) {
						input "Ready to promote to TEST?"
						
						if (openshift.selector("secrets", "classy-dev").exists()) {
							openshift.selector("secrets", "classy-dev").delete()
						}
						if (!openshift.selector("pvc", "postgresql").exists()) {
							
							echo "no PVC found, creating..."
						
							databasePVC = openshift.process(
							readFile(file:"${databaseBC}"))
							
							openshift.apply(databasePVC)
						}
						
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
						
						nginx = openshift.process(
							readFile(file:"${nginxDC}"),
							"-p",
							"APP_NAME=${APP_NAME}", 
							"NAME_SUFFIX=${DEV_SUFFIX}-${PR_NUM}", 
							"ENV_NAME=${DEV_SUFFIX}", 
							"APP_IMAGE_TAG=${PR_NUM}",
							"APPLICATION_DOMAIN=${APP_NAME}-${DEV_SUFFIX}.pathfinder.gov.bc.ca")
						
						
						openshift.apply(database)
							.label(['app':"classy-${DEV_SUFFIX}-${PR_NUM}", 
							'app-name':"${APP_NAME}", 
							'env-name':"${DEV_SUFFIX}"], 
							"--overwrite")
						
						openshift.apply(backend)
							.label(['app':"classy-${DEV_SUFFIX}-${PR_NUM}", 
							'app-name':"${APP_NAME}", 
							'env-name':"${DEV_SUFFIX}"], 
							"--overwrite")

						openshift.apply(nginx)
							.label(['app':"classy-${DEV_SUFFIX}-${PR_NUM}", 
							'app-name':"${APP_NAME}", 
							'env-name':"${DEV_SUFFIX}"], 
							"--overwrite")
		

					}
				}
			}
		}
	
	}*/
  }//end of stages
}//pipeline end


		  
/*
    SONARQUBE_PWD = getSonarQubePwd().trim()
  
  }
  agent any
  stages {
    stage('Checkout Source') {
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
						// ======================================================================================================
						// Set your SonarQube scanner properties at this level, not at the Gradle Build level.
						// The only thing that should be defined at the Gradle Build level is a minimal set of generic defaults.
						//
						// For more information on available properties visit:
						// - https://docs.sonarqube.org/display/SCAN/Analyzing+with+SonarQube+Scanner+for+Gradle
						// ======================================================================================================
						
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
*/
