#include <pthread.h>

int shared_variable = 0;
pthread_mutex_t m;

void *thread_test(void *args)
{
    while (shared_variable < 5)
    {
        shared_variable += 1;
    }
    return (void*)NULL;
}

int main()
{
    pthread_t t1;
    pthread_create(&t1, NULL, thread_test, NULL);
    pthread_join(t1, NULL);
    return 0;
}
