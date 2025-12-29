package main

import (
	"log"

	"github.com/aws/aws-lambda-go/lambda"
	"github.com/fermar8/bball-app-template/internal/handler"
)

func main() {
	log.Println("Starting Lambda function...")
	lambda.Start(handler.HandleRequest)
}
