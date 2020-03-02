#include <stdio.h>
#include <threads.h>

static void *nested_thread()
{
    printf("Start nested thread\n");
    static int i = 0;
    printf("End nested thread with value: %d\n", i);
	return (void*)NULL;
}

void *thread_test(void *args)
{
    printf("Start thread\n");
    pthread_t t2;
    pthread_create(&t2, NULL, nested_thread, NULL);
    printf("I'm in the middle\n");
    pthread_join(t2, NULL);
    printf("End thread\n");
    return (void*)NULL;
}
