#include <stdio.h>

int main()
{
    int user_choice;
    scanf("%d", &user_choice);
    switch(user_choice)
    {
        case 0:
            break;
        case 1:
        case 2:
            if (user_choice == 1)
            {
                printf("You are the new one user!");
            }
            else
            {
                printf("There are two of you!");
            }
            break;

        default:
            if (user_choice % 2)
                printf("One of you does not have a pair!");
            else
                printf("You are creating pairs! Good!");
    }
    return 0;
}
