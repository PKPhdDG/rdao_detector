#include <pthread.h>
#include <stdio.h>

int shared_variable = 100;
pthread_mutex_t m;

void *thread(void *args)
{
	pthread_mutex_lock(&m);
    for(;shared_variable;--shared_variable);
	pthread_mutex_unlock(&m);
    return (void*)NULL;
}

int main()
{
    pthread_t t1;
    pthread_create(&t1, NULL, thread, NULL);
	printf("%d", shared_variable);
    pthread_join(t1, NULL);
    return 0;
}
