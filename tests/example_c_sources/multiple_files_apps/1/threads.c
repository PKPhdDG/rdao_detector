#include <threads.h>

pthread_mutex_t m;

static bool check_access(const char *fname)
{
    bool value = false;
    pthread_mutex_lock(&m);
    value = access(fname, F_OK) != -1;
    pthread_mutex_unlock(&m);
    return value;
}

static bool write_to_file(const char *fname, const char *data)
{
	FILE *file_handler;
    pthread_mutex_lock(&m);
	if(!(file_handler = fopen(fname, "w")))
	{
        pthread_mutex_unlock(&m);
		return false;
	}
	fprintf(file_handler, "%s", data);
	fclose(file_handler);
    pthread_mutex_unlock(&m);
    return true;
}

void* t1f(void *args)
{
	const char *fname = (const char *)args;
    if (check_access(fname)) write_to_file(fname, "Thread 1");
	return NULL;
}

void* t2f(void *args)
{
	const char *fname = (const char *)args;
    write_to_file(fname, "Thread 2");
	return NULL;
}
