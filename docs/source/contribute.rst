Contribute
===============

This document explains how you can contribute to this project.

It assumes you know a minimum of Python and Git.


The mailing-list
-----------------

.. _mailing-list: https://groups.google.com/forum/#!forum/public-contracts

The mailing-list_ is the place to communicate in this project.


Ticket system
-----------------

.. _`ticket system`: https://github.com/jorgecarleitao/public-contracts/issues

This project uses a `ticket system`_ for documenting issues.

The system's idea is to keep track of the issues the project has,
which are being address, and by whom.

Adding tickets is thus a fundamental part of this project:
any improvement starts by finding something that can be improved.

We prefer using the ticket system to communicate about specific
issues, and the mailing-list_ to broader topics such as new features or changing the existing API.

Adding tickets
:::::::::::::::::

We write tickets with clear, concise and specific information about issue we are addressing
and, as rule of thumb, we add a label of each color to the ticket.

We address tickets the same way we would like a ticket of ours to be addressed.

Ticket triage
:::::::::::::::::

When a ticket is added, it enters a triage phase. In this process, the fate of the ticket is decided.

There are 3 main possible outcomes for the ticket:

- The ticket is rejected: it is a duplicate, invalid, or it does not show to be of enough value to the project.
- The ticket is postponed: the ticket is valid but the cost of addressing it is far higher than the value it provides, thus becoming something that should be discussed on a later time.
- The ticket is accepted: the ticket is valid and shows a high value over cost ratio that makes it appealing to work in.

No one likes to have a ticket rejected, so, please, consider giving constructive suggestions to the ticket,
specially when you think the ticket should be rejected. For instance, suggest the user to use the mailing list
if he is really passionate about his idea.

Working tickets
::::::::::::::::::

Working on the ticket means the contributor is committing himself to modify to the source to fulfill the ticket
expectations.

We give the chance to contributors - specially to new contributors -
to go thought the full process: if the person who submitted the ticket is willing to work on it,
he should have priority on doing it, even if this means having the ticket open for a longer time.

If there is more than one contributor interested in working on a ticket, they should make an effort to work together.

Closing tickets
::::::::::::::::

When a ticket is fixed, normally by a commit or set of commits, it is closed as fixed. A ticket can be re-opened
if there is no consensus that it was solved.

Obtaining and modifying the source
-----------------------------------

.. _GitHub: https://github.com/jorgecarleitao/public-contracts

The source can be obtained by forking or cloning it in GitHub_.

Code styling
::::::::::::::::::

1. We follow PEP 8
2. We capitalize the first letter of classes.
3. We import modules in the following order:

    1. system modules
    2. Django modules
    3. other third party modules
    4. project modules
    5. app modules

4. We don't use::

    from X import *

5. We comment and document directly the source code only when necessary to understand what it means within its context.
I.e. the big picture is documented in this documentation.

.. hint:: Making the code clearer and better documented is a good way of start contributing to this project since
    you read code and try to make it more clear when you don't understand it.

Documentation
::::::::::::::::::

The API of this project is expected to be fully documented, i.e., this documentation **is**
part of the project. If you find a mistake, please help us out by filling a ticket in the `ticket system`_.

A modification on the code that changes semantics of the project
has to be accompanied by the respective change in documentation to be incorporated.

.. hint:: Improving the documentation is a good way to start contributing to the project, since you learn
    about the project while improving it.


Committing
---------------------

When you feel that your changes provide value to the existing code, you should commit them.

Commit message
:::::::::::::::::::

We use 72 characters limit to the first line of the commit message. If you see that you are passing
this number, consider dividing the commit in two, as most likely it represents two different things.

A commit is self contained: the first message explains what it does, the rest of the lines explain how and what
changed specifically. The actual code changes of the commit support what the commit message says.

When the commit fixes a given ticket, it must contain that information on the commit message.

Pull requests
----------------

When you have a commit or set of commits that you fell they are worth to be incorporated (most likely
because they close a specific ticket), you should make a pull request to announce that you have value that can be
added to the project.

requesting a pull
::::::::::::::::::

We prefer the GitHub way: you push your local commits to your GitHub fork, and create a pull request from there.

The message of the pull request should be equivalent to a message for a commit, except that it should now be a
message that explains that set of commits (and not the commit itself).

In case you don't use GitHub, you can also create a patch and attach it to a ticket to submit it.

Pull request/patch review
::::::::::::::::::::::::::

The idea of the pull request is that you are notifying other contributors that you have a set of commits that
are worth adding to the project.

As such, it is worth to have the pull request reviewed by other contributors before entering
the project's source. The idea is that other persons can check what you did.

A pull request is a big step for any contributor. It is a piece of work that deserves respect.
Consequently, we ask everyone to be particularly constructive in the review process, specially
when addressing mistakes.
