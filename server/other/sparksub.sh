curl -X POST http://localhost:6066/v1/submissions/create --header "Content-Type:application/json;charset=UTF-8" --data '{
"action" : "CreateSubmissionRequest",
"appArgs" : [ "10" ],
"appResource" : "file:/home/user/spark-2.1.0h/examples/src/main/python/pi.py",
"clientSparkVersion" : "1.6.0",
"environmentVariables" : {
"SPARK_ENV_LOADED" : "1"
},
"mainClass" : "pi",
"sparkProperties" : {
"spark.jars" : "file:/home/user/spark-2.1.0h/examples/src/main/python/pi.py",
"spark.driver.supervise" : "false",
"spark.app.name" : "MyPiJob",
"spark.eventLog.enabled": "true",
"spark.submit.deployMode" : "local",
"spark.master" : "spark://localhost:6066"
}
}'

