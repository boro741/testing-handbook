Feature: Assign a task to a project member
  As a project member
  I want to assign a task to a teammate
  So that everyone knows who owns it

  Scenario: Assign a task to a member of the project
    Given alice is logged in
    And a task exists in the Demo project
    When alice assigns the task to bob
    Then the response status is 200
    And the task assignee is bob

  Scenario: Assign a task to someone who is not a member of the project
    Given alice is logged in
    And a task exists in a project that only alice belongs to
    When alice assigns the task to bob
    Then the response status is 422
    And the task has no assignee
