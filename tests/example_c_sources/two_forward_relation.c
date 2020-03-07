#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char *shared_variable;
char *shared_variable2;

void *thread_test(void *args)
{
    const char text[] = "password: 1234";
    const char text2[] = "password: 98765";
    const size_t size = strlen(text);
    const size_t size2 = strlen(text2);
    shared_variable = (char*)malloc(size * sizeof(char));
    shared_variable2 = (char*)malloc(size2 * sizeof(char));
    memcpy(shared_variable, text, size);
    memcpy(shared_variable2, text2, size2);
    memset(&shared_variable[10], '*', size-10);
    memset(&shared_variable2[10], '*', size2-10);
    for(int i=0; i < size; ++i)
    {
        printf("%c", shared_variable[i]);
    }
    printf("\n");
    for(int i=0; i < size; ++i)
    {
        printf("%c", shared_variable2[i]);
    }
    free(shared_variable);
    free(shared_variable2);
    return (void*)NULL;
}

int main()
{
    pthread_t t1;
    pthread_create(&t1, NULL, thread_test, NULL);
    pthread_join(t1, NULL);
    return 0;
}
