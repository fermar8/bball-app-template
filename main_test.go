package main

import (
	"context"
	"testing"
)

func TestHandleRequest(t *testing.T) {
	ctx := context.Background()
	
	// Test with nil event
	result, err := HandleRequest(ctx, nil)
	
	if err != nil {
		t.Errorf("HandleRequest returned an unexpected error: %v", err)
	}
	
	if result != "Success" {
		t.Errorf("HandleRequest returned unexpected result: got %v, want %v", result, "Success")
	}
}

func TestHandleRequestWithEvent(t *testing.T) {
	ctx := context.Background()
	
	// Test with a simple event
	event := map[string]interface{}{
		"key": "value",
	}
	
	result, err := HandleRequest(ctx, event)
	
	if err != nil {
		t.Errorf("HandleRequest returned an unexpected error: %v", err)
	}
	
	if result != "Success" {
		t.Errorf("HandleRequest returned unexpected result: got %v, want %v", result, "Success")
	}
}
