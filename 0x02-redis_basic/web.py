#!/usr/bin/env python3
'''A module with tools for request caching and tracking.
'''
import redis
import requests
from functools import wraps
from typing import Callable

# Create a Redis client
redis_store = redis.Redis()

def data_cacher(method: Callable) -> Callable:
    '''Caches the output of fetched data and tracks access counts.
    '''
    @wraps(method)
    def invoker(url: str) -> str:
        '''The wrapper function for caching the output and tracking access counts.
        '''
        # Increment the count for the URL
        redis_store.incr(f'count:{url}')
        
        # Check if the URL's data is cached
        cached_page = redis_store.get(f'result:{url}')
        if cached_page:
            return cached_page.decode('utf-8')
        
        # Fetch the URL data and cache it with expiration
        result = method(url)
        redis_store.setex(f'result:{url}', 10, result)
        return result
    return invoker

@data_cacher
def get_page(url: str) -> str:
    '''Returns the content of a URL after caching the request's response
    and tracking the request.
    '''
    response = requests.get(url)
    return response.text

# Test the caching and tracking
if __name__ == "__main__":
    test_url = "http://slowwly.robertomurray.co.uk"
    print(get_page(test_url))
    print(get_page(test_url))  # Should use the cached result
    print(f"Access count for {test_url}: {redis_store.get(f'count:{test_url}').decode('utf-8')}")
