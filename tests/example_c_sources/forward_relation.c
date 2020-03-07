#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char *shared_variable;

void *thread_test(void *args)
{
    const char text[] = "password: 1234";
    const size_t size = strlen(text);
    shared_variable = (char*)malloc(size * sizeof(char));
    memcpy(shared_variable, text, size);
    memset(&shared_variable[10], '*', size);
    for(int i=0; i < size; ++i)
    {
        printf("%c", shared_variable[i]);
    }
    free(shared_variable);
    return (void*)NULL;
}

int main()
{
    pthread_t t1;
    pthread_create(&t1, NULL, thread_test, NULL);
    pthread_join(t1, NULL);
    return 0;
}
