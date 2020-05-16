#include <stdio.h>

int main()
{
    int i=0;
    while (i < 100)
    {
        if (i > 99)
            break;
        else
            printf("%d\n", i);
        ++i;
    }

    return 0;
}
