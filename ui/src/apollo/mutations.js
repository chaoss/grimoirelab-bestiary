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

export { addProject };
