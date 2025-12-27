package main

import (
	"context"
	"log"

	"github.com/aws/aws-lambda-go/lambda"
)

// HandleRequest processes the Lambda event
func HandleRequest(ctx context.Context, event interface{}) (string, error) {
	log.Println("Processing template handler")
	return "Success", nil
}

func main() {
	lambda.Start(HandleRequest)
}
