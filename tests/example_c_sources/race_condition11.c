#include <stdio.h>
#include <pthread.h>

static volatile long long r1;

void* deposit2(void *args) {
    for (int i=0; i<1000000; i++)
    {
        ++r1;
    }
    return NULL;
}

void* deposit1(void *args) {
    const int number_of_threads = 15;
    pthread_t threads[number_of_threads];
    printf("Status: %lld\r\n", r1);
    for (size_t i=0; i < number_of_threads; ++i)
        pthread_create(&threads[i], NULL, deposit2, NULL);

    for (size_t i=0; i < number_of_threads; ++i)
        pthread_join(threads[i], NULL);
    printf("Status: %lld\r\n", r1);
    return NULL;
}

int main() {
    pthread_t thread;
    pthread_create(&thread, NULL, deposit1, NULL);
    printf("App start work with r1 = %lld\r\n", r1);
    pthread_join(thread, NULL);
    printf("App finish work with r1 = %lld\r\n", r1);
    return 0;
}
