package handler

import (
	"context"
	"log"
)

func HandleRequest(ctx context.Context, event interface{}) (string, error) {
	log.Println("Processing template handler")
	return "Success", nil
}
