=====================
 Project task subtask
=====================

Usage
=====

How to check that module works:
* Create user1 and user2: open menu ``Settings >> Users`` click ``[Create]`` in ``Technical Settings`` select "Task's Work on Tasks", in ``Application`` select "Project: user"
* Login as user1, open ``Project >> Tasks >> Subtasks`` and create new subtask( Reviewer is user1, Assiigned to user2)
* Login as user2, you can see message in Inbox "todo: subtask_name", change state of subtask to cancelled/done
* As user2 you can see message in Inbox "cancelled/done: subtask_name" 
* In ``Project >> Tasks`` kanban view displays all subtasks in state "todo" assigned to you and subtasks where you are a Reviewer 
* In ``Project >> Subtasks`` displays all subtask in all states assigned to you and subtasks where you are a Reviewer, also you can find subtasks with the help of filters "My" and "Todo"
