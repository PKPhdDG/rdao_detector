#include <stdio.h>
#include <threads.h>

static void *nested_thread3()
{
    return (void*)NULL;
}

static void *nested_thread2()
{
    pthread_t t5;
    pthread_create(&t5, NULL, nested_thread3, NULL);
    pthread_join(t5, NULL);
    return (void*)NULL;
}

static void *nested_thread1()
{
    pthread_t t4;
    pthread_create(&t4, NULL, nested_thread3, NULL);
    pthread_join(t4, NULL);
    return (void*)NULL;
}

void *thread_test(void *args)
{
    pthread_t t2, t3;
    pthread_create(&t2, NULL, nested_thread1, NULL);
    pthread_create(&t3, NULL, nested_thread2, NULL);
    pthread_join(t2, NULL);
    pthread_join(t3, NULL);
    return (void*)NULL;
}
