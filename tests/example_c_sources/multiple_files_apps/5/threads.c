#include <stdio.h>
#include <threads.h>

static void *nested_thread()
{
    printf("Start nested thread\r\n");
    static int i = 0;
    printf("End nested thread with value: %d\r\n", i);
	return (void*)NULL;
}

void *thread_test(void *args)
{
    printf("Start thread\r\n");
    pthread_t t2;
    pthread_create(&t2, NULL, nested_thread, NULL);
    printf("I'm in the middle\n");
    pthread_join(t2, NULL);
    printf("End thread\r\n");
    return (void*)NULL;
}
