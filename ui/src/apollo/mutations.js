import gql from "graphql-tag";

const ADD_PROJECT = gql`
  mutation addProject(
    $ecosystemId: ID
    $name: String
    $title: String
    $parentId: ID
  ) {
    addProject(
      ecosystemId: $ecosystemId
      name: $name
      title: $title
      parentId: $parentId
    ) {
      project {
        id
        name
      }
    }
  }
`;

const DELETE_PROJECT = gql`
  mutation deleteProject($id: ID) {
    deleteProject(id: $id) {
      project {
        id
      }
    }
  }
`;

const addProject = (apollo, data) => {
  const response = apollo.mutate({
    mutation: ADD_PROJECT,
    variables: {
      ecosystemId: data.ecosystemId,
      name: data.name,
      title: data.title,
      parentId: data.parentId
    }
  });
  return response;
};

const deleteProject = (apollo, id) => {
  const response = apollo.mutate({
    mutation: DELETE_PROJECT,
    variables: {
      id: id
    }
  });
  return response;
};

export { addProject, deleteProject };
