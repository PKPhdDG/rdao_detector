#include <stdio.h>
#include <pthread.h>

static volatile int r1 = 0;

void* deposit1(void *args) {
    printf("Status: %d", r1);
    for (int i=0; i<1000000; i++)
    {
        ++r1;
    }
    printf("Status: %d", r1);
    return NULL;
}

int main() {
    const int number_of_threads = 2;
    pthread_t threads[number_of_threads];
    printf("App start work with r1 = %d\n", r1);

    for (size_t i=0; i < number_of_threads; ++i)
        pthread_create(&threads[i], NULL, deposit1, NULL);

    for (size_t i=0; i < number_of_threads; ++i)
        pthread_join(threads[i], NULL);

    printf("App finish work with r1 = %d\n", r1);
    return 0;
}
