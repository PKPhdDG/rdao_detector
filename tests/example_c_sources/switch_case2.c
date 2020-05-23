#include <stdio.h>

int main()
{
    int user_choice;
    scanf("%d", &user_choice);
    switch(user_choice)
    {
        case 0:
            printf("You choosed 0!\n");
            break;
        case 1:
            printf("You choosed 1!\n");
            break;
        default:
            printf("You did not choose correct value!\n");
    }

    printf("Thank you my user!\n");
    return 0;
}
